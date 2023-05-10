from enum import Enum
import sys, os
import re
import shutil
from typing import List, Optional, Tuple, Union
from PIL import Image
from PyPDF2 import PdfReader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings.settings import settings
from data.dataset import Dataset, HelperMode
from logger import Logger

class DatasetHelper():
    def __init__(
        self, 
        logger: Logger,
        input_folder: str,
        output_folder: str,
        helper_mode: HelperMode
    ) -> None:
        self.logger        = logger
        self.input_folder  = input_folder
        self.output_folder = output_folder
        self.helper_mode   = helper_mode


    def get_available_datasets(self) -> List[Dataset]:
        """
        Retrieves all available datasets in the input folder and returns them as a list of Dataset objects.
        A dataset is considered available if it is a directory and its completeness meets the requirements of
        the provided HelperMode. If a dataset is not complete, it will be skipped.
        """
        self.logger.log(f"Retrieving available datasets...")

        # Create empty list for the available datasets
        available_dataset_objects = []

        # Loop through everything in the input folder (files/folders)
        for dataset_name in os.listdir(self.input_folder):
            # Create the full path of the dataset
            dataset_path = os.path.join(self.input_folder, dataset_name)

            # Check if the created path is a directory
            if os.path.isdir(dataset_path):
                # Create a dataset object
                dataset = self.create_dataset_object(dataset_path)

                # Check if the dataset object is complete for the respective mode
                dataset_is_complete = dataset.is_complete(self.helper_mode)
                if dataset_is_complete:
                    self.logger.log(f"  {dataset_name} is complete")
                    # Append the complete dataset to the list
                    available_dataset_objects.append(dataset)
                else:
                    self.logger.log(f"  {dataset_name} is incomplete")

        self.logger.log(f"Total available datasets: {len(available_dataset_objects)}")
        return available_dataset_objects

    
    def create_dataset_object(self, dataset_path: str) -> Dataset:
        """
        This method creates a new Dataset object from the given dataset_path. No checks are made to ensure the dataset 
        exists. To determine whether the dataset is complete and can be used for calculation or export, use the methods 
        dataset.is_complete_for_calculation() and dataset.is_complete_for_export(), respectively.
        """
        # Get all the needed dataset attributes 
        dataset_name        = os.path.basename(dataset_path)
        image_folder_path   = os.path.join(dataset_path, settings['image_folder_path'])
        model_folder_path   = os.path.join(dataset_path, settings['model_folder_path'])
        cam_pos_file_path   = os.path.join(dataset_path, settings['cam_pos_file_path'])
        scan_info_file_path = os.path.join(dataset_path, settings['scan_info_file_path'])
        psx_file_path       = os.path.join(model_folder_path, f"{dataset_name}.psx")
        obj_file_path       = os.path.join(model_folder_path, f"{dataset_name}.obj")
        f_number            = self.get_f_number(scan_info_file_path)
        image_paths         = self.get_image_paths(image_folder_path)
        image_size          = self.get_first_image_size(image_paths)
        needed_image_count  = self.get_needed_image_count(scan_info_file_path)
        

        # Create dataset object with the attributes
        dataset = Dataset(
            dataset_name,
            dataset_path,
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
    

    def get_image_paths(self, image_folder_path: str) -> List[str]:
        """
        This method returns a list of all image paths in a specified folder.
        """
        image_paths = []
        # Add the images to the image paths list
        if os.path.exists(image_folder_path):
            for entry in os.scandir(image_folder_path):
                if entry.is_file() and entry.name.lower().endswith(tuple(settings['image_extensions'])):
                    image_paths.append(entry.path)
        # Return the image list
        return image_paths


    def get_needed_image_count(self, scan_info_file_path: str) -> Optional[int]:
        """
        This method is used to extract the needed image count from the scan information pdf. 
        If the num images could not be extracted or it is 0 it returns None.
        """
        try:
            with open(scan_info_file_path, "rb") as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                pdf_text = pdf_reader.pages[0].extract_text()
            cleaned_pdf_text = self.clean_pdf_text(pdf_text)
            match = re.search(settings.get('num_images_regex'), cleaned_pdf_text)
            if match:
                num_images = int(match.group(1))
                if num_images > 0:
                    return num_images
        except:
            pass
        return None
    

    def get_first_image_size(self, image_paths: List[str]) -> Optional[Tuple[int, int]]:
        """
        This method is used to retrieve the size of the first image.
        If the image size cannot be accessed or is not a tuple of two integers, it returns None.
        """
        try:
            # Open the first image and get the image size (width, height)
            with Image.open(image_paths[0]) as image:
                width, height = image.size
                if isinstance(width, int) and isinstance(height, int):
                    return width, height
        except:
            pass
        return None


    def get_f_number(self, scan_info_file_path) -> Optional[float]:
        """
        This method is used extract the f number from the scan information file 
        """
        try:
            with open(scan_info_file_path, "rb") as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                pdf_text = pdf_reader.pages[0].extract_text()
            cleaned_pdf_text = self.clean_pdf_text(pdf_text)
            match = re.search(settings.get('f_number_regex'), cleaned_pdf_text)
            if match:
                return float(match.group(1))
        except Exception as e:
            pass
        return None
    
    
    def clean_pdf_text(self, pdf_text: str) -> str:
        """
        This method is used to remove \n (newline) and unnecessary spaces from pdf text.
        """
        # replace all \n with a space
        cleaned_pdf_text = re.sub('\n', ' ', pdf_text)
        # replace all multiple spaces with one space
        cleaned_pdf_text = re.sub(' +', ' ', cleaned_pdf_text)

        # replace all spaces after colon
        cleaned_pdf_text = re.sub(r":\s+", ":", cleaned_pdf_text)

        return cleaned_pdf_text


    def move_dataset(self, dataset: Dataset) -> None:
        """
        This method is used to move processed datasets into the output folder
        """
        # Check if the dataset path is a directory
        if not os.path.isdir(dataset.basepath):
            raise ValueError("The dataset path does not exist or is not a directory")
        # Check if the output folder path is a directory
        if not os.path.isdir(self.output_folder):
            raise ValueError("The output folder does not exist or is not a directory")
        # Move the dataset to the output folder
        shutil.move(dataset.basepath, self.output_folder)
        self.logger.log(f"   Dataset moved to '{self.output_folder}'")
