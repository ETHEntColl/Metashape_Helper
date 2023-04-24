#----------------------------------------
# Metashape helpers settings
# Code by S. Bär - April 2023
#----------------------------------------
# SETTINGS AND THEIR PURPOSE:
#   
#   SCRIPT SETTINGS:
#   ================
#   script_api_version  -> Used to check compatibility of the script with the installed Metashape version
#       
#   LOG SETTINGS:
#   ============
#   log_output_folder_path -> Path where the log files should be stored
#
#   DATASET STRUCTURE SETTINGS:
#   ==========================
#   use_folder_prefix   -> Used if you want to select datasets with a certain prefix only
#   folder_prefixes     -> Dataset prefixes that are accepted
#   model_folder_path   -> Location of the model folder (relative to dataset folder)
#   image_folder_path   -> Location of the image folder (relative to dataset folder)
#   image_extensions    -> Image types that are used eg. png, jpeg, etc.
#   cam_pos_file_path   -> Location of the cam position file (relative to dataset folder)
#   scan_info_file_path -> Location of the scan information file (relative to dataset folder)
#
#   INPUT OUTPUT FOLDER SETTINGS:
#   ============================
#   calculation_input_folder_path   -> Location of the 1_SCANNED folder (absolute path)
#   calculation_output_folder_path  -> Location of the 2_CALCULATED folder (absolute path)
#   export_input_folder_path        -> Location of the 3_UNPINNED folder (absolute path)
#   export_output_folder_path       -> Location of the 4_EXPORTED folder (absolute path)
# 
#   # CALCULATION SETTINGS:
#   use_tweaks          -> Wether to use tweaks or not during the calculation. If you dont want to use tweaks just set it to False
#   tweaks              -> List of tweaks that are used to calculate the model. If you dont want to use tweaks just set use_tweaks to False
#   depthmap_downscale  -> Downscale factor of the depthmaps (0 = no downscale, 0 < = more down scaled)
#
#   EXPORT SETTINGS: 
#   ===============
#   image_texture_size -> Size of the exported texture (width and height are the same)
#
#----------------------------------------

settings = {
    # Script settings
    "script_api_version": "2.0", # Used to compare script api to installed Metashape version

    # Log settings
    "log_output_folder_path": "C:\\InsectScanner\\Simon Temp\\MetashapeHelper\\test\\logs",

    # Dataset structure settings
    "use_folder_prefix": True, 
    "folder_prefixes": ["ETHZ-ENT", "EXP"],
    "model_folder_path": "Model",
    "image_folder_path": "edof",
    "image_extensions": [".png", ".jpg", ".jpeg", ".tif", ".tiff"],
    "cam_pos_file_path": "CamPos.txt",
    "scan_info_file_path": "ScanInformation.pdf",
    
    # Helper input & output folders
    "calculation_input_folder_path":  "C:\\InsectScanner\\Simon Temp\\MetashapeHelper\\test\\data\\1_SCANNED",
    "calculation_output_folder_path": "C:\\InsectScanner\\Simon Temp\\MetashapeHelper\\test\\data\\2_CALCULATED",
    "export_input_folder_path":       "C:\\InsectScanner\\Simon Temp\\MetashapeHelper\\test\\data\\3_UNPINNED",
    "export_output_folder_path":      "C:\\InsectScanner\\Simon Temp\\MetashapeHelper\\test\\data\\4_EXPORTED",

    # Calculation settings
    "use_tweaks": True,
    "tweaks": [("ooc_surface_blow_up",  "0.95"), ("ooc_surface_blow_off", "0.95")],
    "depthmap_downscale": 0,

    # Export settings
    "image_texture_size": 4096
}