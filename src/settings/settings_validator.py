import os
import re
from typing import List
import Metashape

from settings.settings import settings
from settings.settings_exceptions import SettingNotFoundError, SettingTypeError, SettingValueError, MetashapeVersionMismatchError

class SettingsValidator:
    def __init__(self):
        # Used for type checks
        self.settings_types = {
            # Script settings
            'script_api_version': str,
            
            # Log settings
            'log_output_folder_path': str,

            # Dataset structure settings
            'use_folder_prefix': bool,
            'folder_prefixes': List,
            'model_folder_path': str,
            'image_folder_path': str,
            'image_extensions': List,
            'cam_pos_file_path': str,
            'scan_info_file_path': str,

            # Scan info pdf regex
            "f_number_regex": str,
            "num_images_regex": str,

            # Helper input & output folders
            'calculation_input_folder_path': str,
            'calculation_output_folder_path': str,
            'export_input_folder_path': str,
            'export_output_folder_path': str,

            # Calculation settings
            'use_tweaks': bool,
            'tweaks': List,
            'depthmap_downscale': int,
            'use_smooth': bool,

            # Export settings
            'image_texture_size': int,
        }

    def validate(self):
        self.validate_existence()
        self.validate_types()
        self.validate_special_cases()

    def validate_existence(self):
        for setting_name in self.settings_types.keys():
            setting_value = settings.get(setting_name)
            if setting_value is None:
                raise SettingNotFoundError(f"{setting_name} not found!")

    def validate_types(self):
        for setting_name, expected_type in self.settings_types.items():
            setting_value = settings.get(setting_name)
            if not isinstance(setting_value, expected_type):
                raise SettingTypeError(f"Invalid type for setting '{setting_name}'. Expected {expected_type.__name__}, but got {type(setting_value).__name__}!")

    def validate_special_cases(self):
        self.validate_script_api_version()
        self.validate_use_folder_prefix()
        self.validate_image_extensions()
        self.validate_use_tweaks()
        self.validate_folders()
        self.validate_regexes()

    def validate_script_api_version(self):
        script_api_version = settings.get('script_api_version')
        metashape_version  = Metashape.app.version
        if not metashape_version.startswith(script_api_version):
            raise MetashapeVersionMismatchError(metashape_version, script_api_version)

    def validate_use_folder_prefix(self):
        use_folder_prefix = settings.get('use_folder_prefix')
        folder_prefixes   = settings.get('folder_prefixes')
        if use_folder_prefix and len(folder_prefixes) == 0:
            raise SettingValueError("You want to use prefixes but you provided no prefixes.")

    def validate_image_extensions(self):
        image_extensions = settings.get('image_extensions')
        if len(image_extensions) == 0:
            raise SettingValueError("No image extensions have been defined!")

    def validate_use_tweaks(self):
        use_tweaks = settings.get('use_tweaks')
        tweaks     = settings.get('tweaks')
        if use_tweaks and len(tweaks) == 0:
            raise SettingValueError("No tweaks have been defined!")

    def validate_folders(self):
        folder_names = [
            'log_output_folder_path',
            'calculation_input_folder_path',
            'calculation_output_folder_path',
            'export_input_folder_path',
            'export_output_folder_path'
        ]

        for folder_name in folder_names:
            folder_path = settings.get(folder_name)
            if not os.path.exists(folder_path):
                raise FileNotFoundError(f"The {folder_name} : '{folder_path}' does not exist!")
            
    def validate_regexes(self):
        regexes = ['f_number_regex', 'num_images_regex']
        for regex in regexes:
            regex_pattern = settings.get(regex)
            try:
                re.compile(regex_pattern)
            except:
                raise SettingValueError(f"{regex} is not valid regular expression!")