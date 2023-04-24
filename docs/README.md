
# Metashape Helper

## Introduction
We are in the process of digitalizing our insect types in the [Entomological Collection](https://usys.ethz.ch/en/research/collections/entomological-collection.html) at ETH with a 3d-scanner from [Small World Vision](https://small-world-vision.de/en/). Our goal is to have a 3d-model (calculated with Metashape) of all our most valuable insects and later make them available for the public using a 3d-viewer.

Initially, we had to manually carry out each step in Metashape to create the 3D model, which was tedious and time-consuming.

To improve our productivity, we developed some [Metashape scripts](https://github.com/kizvki/Insect-Scanner/tree/main/Metashape/Script/Version%201.8) that automate many of the repetitive tasks. These scripts were already very useful and expedited the entire process. However, they had to be executed manually within the Metashape software, and the settings had to be adjusted every time we recalibrated the scanner.

To simplify our work even further, we created this project. It is tailored to our new scanning workflow.


## Dataset structure

The datasets we get from the 3D-Scanners have the following structure:

```
ETHZ-ENT0574269                     --> Dataset folder with unique number
├── edof                            --> Image folder (extended depth of focus)
│ ├── image_0001_-70_0.png          --> Edof image
│ ├── image_0002_-70_29.2.png       --> Edof image
│ ├── image_0003_-70_58.4           --> Edof image
│ └── ...                           --> 393 more edof images
├── scanInformation.pdf             --> File with scan parameters
└── camPos.txt                      --> File with camera positions
```

## Folder Workflow
We use four folders to indicate the dataset's state. Every dataset will pass through each folder.

```
1_SCANNED      --> Here are all uncalculated datasets (directly from scanner) stored.
2_CALCULATED   --> Here are all calculated datasets (calculated with the calculation helper) stored.
3_UNPINNED     --> Here are all unpinned datasets (pin manually removed from insect) stored.
4_EXPORTED     --> Here are all exported datasets (exported with the export helper) stored.
```

![Folder Workflow](https://github.com/ETHEntColl/Metashape_Helper/blob/main/docs/folders.png)

*Our current workflow*


## Installation

To install the project, follow these steps:

1. Clone the repository with `git clone [repository-url]`.<br /> 
⚠️ ETH network needs proxy `git config http.proxy http://proxy.ethz.ch:3128`.

2. Download the needed Metashape python module [here](https://www.agisoft.com/downloads/installer/).
3. Install the downloaded module file with `pip install [whl-filename]`.
4. Ensure that you activate your metashape license on your system.
5. Adjust the settings in the `src/settings/settings.py` file (most important settings are the folders).

```
settings = {
    # Script settings
    "script_api_version": "2.0",

    # Log settings
    "log_output_folder_path": "C:\\InsectScanner\\Data\\Helper\\Logs",

    # Dataset structure settings
    "use_folder_prefix": True, 
    "folder_prefixes": ["ETHZ-ENT", "EXP"],
    "model_folder_path": "Model",
    "image_folder_path": "edof",
    "image_extensions": [".png", ".jpg", ".jpeg", ".tif", ".tiff"],
    "cam_pos_file_path": "CamPos.txt",
    "scan_info_file_path": "ScanInformation.pdf",
    
    # Helper input & output folders
    "calculation_input_folder_path":  "C:\\InsectScanner\\Data\\DataCurrent\\1_SCANNED",
    "calculation_output_folder_path": "C:\\InsectScanner\\Data\\DataCurrent\\2_CALCULATED",
    "export_input_folder_path":       "C:\\InsectScanner\\Data\\DataCurrent\\3_UNPINNED",
    "export_output_folder_path":      "C:\\InsectScanner\\Data\\DataCurrent\\4_EXPORTED",

    # Calculation settings
    "use_tweaks": True,
    "tweaks": [("ooc_surface_blow_up",  "0.95"), ("ooc_surface_blow_off", "0.95")],
    "depthmap_downscale": 0,

    # Export settings
    "image_texture_size": 4096
}
```

## Usage

To use the two helpers (calculate/export) do the following:

1. Add datasets into the input folders.
2. Execute the needed helper by clicking on the `calculate.bat` or `export.bat` .
3. Wait until the helper has finished processing the datasets or cancel the process by closing the window

If there has been an error you can check out the log file.

## How it works

### Basic process
1. The settings from the settings.py are validated (`settings_validator.py`)
2. The window of is created (`helper_window.py` & `tkinter_helper.py`)
3. A new thread is created for the calculation/export (`calculate.py/export.py`)
2. The datasets are retrieved from the calculation/export input folder (by `dataset_helper.py`)
3. All datasets are calculated/exported (by `metashape_helper.py`)
4. The calculated/exported detasets are moved to the calculation/export output folder (by `dataset_helper.py`)

## Contributing

Any contributions are greatly appreciated.

If you have a suggestion, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/NewFeature`)
3. Commit your Changes (`git commit -m 'Add some NewFeature'`)
4. Push to the Branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Contact
Dr. Michael Greeff - michael.greeff@usys.ethz.ch

Christian Felsner - christian.felsner@usys.ethz.ch

Simon Bär - simon.tobias.baer@gmail.com

