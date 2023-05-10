from enum import Enum
import sys, os
from typing import List, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings.settings import settings

class HelperMode(Enum):
    CALCULATION = 1
    EXPORT = 2

class Dataset:
    def __init__(
            self, 
            name : str,
            basepath : str,
            image_folder_path : str,
            model_folder_path : str,
            cam_pos_file_path : str,
            scan_info_file_path : str,
            psx_file_path : str,
            obj_file_path : str,
            images : List[str],
            f_number : float,
            image_size : Tuple[int],
            needed_image_count: int
        ):

        self.name = name
        self.basepath = basepath
        self.image_folder_path = image_folder_path
        self.model_folder_path = model_folder_path
        self.cam_pos_file_path = cam_pos_file_path
        self.scan_info_file_path = scan_info_file_path
        self.psx_file_path = psx_file_path
        self.obj_file_path = obj_file_path
        self.images = images
        self.f_number = f_number
        self.image_size = image_size
        self.needed_image_count = needed_image_count

    def has_valid_name(self) -> bool:
        # Check if the name is valid
        dataset_name = self.name
        prefixes = settings.get('folder_prefixes')
        use_folder_prefix = settings.get('use_folder_prefix')

        prefix_in_name = any(dataset_name.startswith(prefix) for prefix in prefixes)
        has_valid_name = (use_folder_prefix and prefix_in_name) or not use_folder_prefix
        return has_valid_name


    def is_complete(self, mode: HelperMode) -> bool:
        has_valid_name        = self.has_valid_name()
        cam_pos_file_exists   = os.path.isfile(self.cam_pos_file_path)
        scan_info_file_exists = os.path.isfile(self.scan_info_file_path)
        has_f_number          = self.f_number is not None
        has_images            = len(self.images) > 0
        has_image_size        = self.image_size is not None
        has_needed_images     = len(self.images) == self.needed_image_count
        psx_file_exists       = os.path.isfile(self.psx_file_path)
        in_use                = self.in_use()

        # Check if the dataset has the needed things to be calculated
        if mode == HelperMode.CALCULATION:
            is_complete =  all([
                has_valid_name,
                cam_pos_file_exists,
                scan_info_file_exists,
                has_f_number,
                has_images, 
                has_image_size,
                has_needed_images,
                not psx_file_exists or psx_file_exists and not in_use
            ])
        # Check if the dataset has the needed things to be exported
        if mode == HelperMode.EXPORT:
            is_complete =  all([
                has_valid_name,
                psx_file_exists,
                not in_use,
            ])
       
        return is_complete
    
    def in_use(self)-> bool:
        # Check if there is a lock file inside the model.files foler. If one exists the document is in use.
        lockfile_path = os.path.join(self.model_folder_path, f"{self.name}.files", "lock")
        in_use = os.path.isfile(lockfile_path)
        return in_use
