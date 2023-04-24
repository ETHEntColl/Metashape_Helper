import sys, os
import re
import shutil
from typing import List, Tuple, Union
from PIL import Image
from PyPDF2 import PdfReader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings.settings import settings
from data.dataset import Dataset
from logger import Logger


class DatasetHelper():
    def __init__(self, logger: Logger, input_folder: str, output_folder: str) -> None:
        self.logger        = logger
        self.input_folder  = input_folder
        self.output_folder = output_folder

    # Function used to get all available datasets (objects)
    def get_calculation_datasets(self) -> List[Dataset]:
        self.logger.log(f"Retrieving available datasets...")
        dataset_objects = []
        # Go through all elements in the input folder
        for dataset_name in os.listdir(self.input_folder):
            use_folder_prefix = settings.get('use_folder_prefix')
            folder_prefixes   = settings.get('folder_prefixes')
            if not use_folder_prefix or (folder_prefixes and any(dataset_name.startswith(prefix) for prefix in folder_prefixes)):
                dataset_path = os.path.join(self.input_folder, dataset_name)
                # Check if the path is a directory
                if os.path.isdir(dataset_path):
                    # create an object
                    dataset = self.create_dataset_object(dataset_name, dataset_path)
                    # Check if the dataset object is complete (has all needed parameters for the calculation)
                    if dataset.is_complete_for_calculation():
                        self.logger.log(f"  {dataset_name} is complete")
                        # Add the dataset to the dataset object list
                        dataset_objects.append(dataset)
                    else:
                        self.logger.log(f"  {dataset_name} is incomplete")
        self.logger.log(f"Total available datasets: {len(dataset_objects)}")
        return dataset_objects
    
    # Function used to get all available datasets (objects)
    def get_export_datasets(self) -> List[Dataset]:
        self.logger.log(f"Retrieving available datasets...")
        dataset_objects = []
        for dataset_name in os.listdir(self.input_folder):
            use_folder_prefix = settings.get('use_folder_prefix')
            folder_prefixes   = settings.get('folder_prefixes')
            if not use_folder_prefix or (folder_prefixes and any(dataset_name.startswith(prefix) for prefix in folder_prefixes)):
                dataset_path = os.path.join(self.input_folder, dataset_name)
                # Check if the path is a directory
                if os.path.isdir(dataset_path):
                    # create an object
                    dataset = self.create_dataset_object(dataset_name, dataset_path)
                    # Check if the dataset object is complete (has all needed parameters for the export)
                    if dataset.is_complete_for_export():
                        self.logger.log(f"  {dataset_name} is complete")
                        # Add the dataset to the dataset object list
                        dataset_objects.append(dataset)
                    else:
                        self.logger.log(f"  {dataset_name} is incomplete")
        self.logger.log(f"Total available datasets: {len(dataset_objects)}")
        return dataset_objects


    def create_dataset_object(self, dataset_name: str, dataset_path: str) -> Dataset:
        # Get all the needed dataset attributes
        basepath            = dataset_path
        image_folder_path   = os.path.join(basepath, settings['image_folder_path'])
        model_folder_path   = os.path.join(basepath, settings['model_folder_path'])
        cam_pos_file_path   = os.path.join(basepath, settings['cam_pos_file_path'])
        scan_info_file_path = os.path.join(basepath, settings['scan_info_file_path'])
        psx_file_path       = os.path.join(model_folder_path, f"{dataset_name}.psx")
        obj_file_path       = os.path.join(model_folder_path, f"{dataset_name}.obj")
        f_number            = self.get_f_number(scan_info_file_path)
        image_paths         = self.get_image_paths(image_folder_path)
        needed_image_count  = self.get_needed_image_count(scan_info_file_path)
        image_size          = self.get_image_size(image_paths)

        # Create dataset object with the attributes
        dataset = Dataset(
            dataset_name,
            basepath,
            image_folder_path,
            model_folder_path,
            cam_pos_file_path,
            scan_info_file_path,
            psx_file_path,
            obj_file_path,
            image_paths,
            f_number,
            image_size,
            needed_image_count,
        )
        return dataset
    
    # Function used to get all available datasets (objects)
    def get_image_paths(self, image_folder_path: str) -> Union[List[str], None]:
        image_paths = []
        
        # Add the images to the image paths list
        if os.path.exists(image_folder_path):
            for image in os.scandir(image_folder_path):
                if image.is_file() and image.name.lower().endswith(tuple(settings['image_extensions'])):
                    image_paths.append(os.path.join(image_folder_path, image.name))

        # Return None if there are no images
        image_paths = None if len(image_paths) == 0 else image_paths
        return image_paths

    # Function to get the f number from the pdf file
    def get_f_number(self, scan_info_file_path) -> Union[float, None]:
        f_number = None
        try:
            # Try to open the ScanInformation.pdf file and extract the f number
            with open(scan_info_file_path, "rb") as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                if len(pdf_reader.pages) == 0:
                    raise ValueError("ScanInformation.pdf is empty")
                pdf_text = pdf_reader.pages[0].extract_text()
                match = re.search(r"([0-9.]{8})", pdf_text)
                f_number = float(match.group(1))
        except:
            pass
        # Return None or the f_number
        return f_number
    
    # Function to get the image size from the first image
    def get_image_size(self, image_path: str) -> Union[Tuple[int, int], None]:
        image_size = None
        try:
            # Open the first image and get the image size (width, height)
            with Image.open(image_path[0]) as first_image:
                image_size = first_image.size
        except:
            pass
        # Return None if the the imagesize is not a tuple of two ints or the image size tuple
        image_size = None if not isinstance(image_size, tuple) or len(image_size) != 2 or not all(isinstance(x, int) for x in image_size) else image_size
        return image_size


    def get_needed_image_count(self, scan_info_file_path: str) -> Union[int, None]:
        num_images = None
        try:
            # Try to open the ScanInformation.pdf file and extract the needed image count
            with open(scan_info_file_path, "rb") as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                if len(pdf_reader.pages) == 0:
                    raise ValueError("ScanInformation.pdf is empty")
                pdf_text = pdf_reader.pages[0].extract_text()

            match = re.search(r"Num Images: \n([0-9]*)", pdf_text)
            num_images = int(match.group(1))
        except:
            pass
        # Return None if there are 
        num_images = None if num_images == 0 else num_images
        return num_images
    

    # Function used to move processed datasets into the output folders
    def move_dataset(self, dataset: Dataset) -> None:
        # Check if the dataset path is a directory
        if not os.path.isdir(dataset.basepath):
            raise ValueError("The dataset path does not exist or is not a directory")
        # Check if the output folder path is a directory
        if not os.path.isdir(self.output_folder):
            raise ValueError("The output folder does not exist or is not a directory")
        # Move the dataset to the output folder
        shutil.move(dataset.basepath, self.output_folder)
        self.logger.log(f"   Dataset moved to '{self.output_folder}'")
