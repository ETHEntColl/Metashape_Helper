import datetime
import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from data.dataset_helper import DatasetHelper
from gui.helper_window import HelperWindow
from settings.settings import settings
from settings.settings_validator import SettingsValidator
from logger import Logger
from metashape_helper import MetashapeHelper

def export():
    # Make the available_datasets, processed_datasets, and the start_time available locally
    global dataset_helper, available_datasets, processed_datasets, start_time

    try:
        # Get the available datasets
        available_datasets = dataset_helper.get_export_datasets()

        # Raise an exception if there are no available datasets
        if len(available_datasets) == 0:
            raise ValueError(f"No datasets available!")

        # Calculate the progressbar steps
        datasets_done_progressbar_step = 100/len(available_datasets)

        # Calculate the progressbar steps
        window.update_datasets_done(0, len(processed_datasets), len(available_datasets))

        # Loop through every available dataset
        for dataset in available_datasets:
            # Log the dataset name
            logger.log(dataset.name)

            # Display the current dataset name in the gui
            window.current_dataset_name_dynamic_label.configure(text=dataset.name)

            # Create a metashape helper for the dataset and export the the current dataset
            metashape_helper = MetashapeHelper(dataset, window, logger)
            metashape_helper.export()

            # Move the dataset to the output folder
            dataset_helper.move_dataset(dataset)

            # Delete the dataset helper
            del metashape_helper

            # Add the exported dataset to the processed dataset list
            processed_datasets.append(dataset)

            # Update the datasets done progressbar
            window.update_datasets_done(datasets_done_progressbar_step, len(processed_datasets), len(available_datasets))
        
        # Log the processed dataset amount
        log_processed_datasets(show_message_box=True)

    except Exception as e:
        # Log the exception
        logger.log(f'{type(e).__name__}: {e}')
        # Show the error popup
        show_error_popup(e)


def log_processed_datasets(show_message_box: bool):
    # Make the logger, processed_datasets, available_datasets, and the start_time available locally
    global logger, processed_datasets, available_datasets, start_time

    # Store the datasets count
    processed_datasets_count = len(processed_datasets)
    available_datasets_count = len(available_datasets)

    # Get the elapsed time and format it
    end_time       = datetime.datetime.now()
    elapsed_time   = end_time - start_time
    formatted_time = str(elapsed_time).split('.')[0]

    # Create the message
    message = f"Exported {processed_datasets_count} of {available_datasets_count} dataset(s) in {formatted_time} seconds."

    if len(processed_datasets) > 0:
        # Log the message and display a infobox with the processed dataset amount
        logger.log(message)
        if show_message_box:
            messagebox.showinfo("Export complete", message)
            close_helper()
    else:
        logger.log("No datasets have been exported!")


def on_window_close():
    # Make the logger and the window available locally
    global logger, window

    # Ask the user if he really wants to close the helper and abort the export
    if messagebox.askokcancel("Quit", "Do you want to abort export?\n Unfinished progress will be lost!"):
        logger.log(f"Export aborted by user!")
        log_processed_datasets(show_message_box=False)

        # Close the helper
        close_helper()


def close_helper():
    # Make the logger and the window available locally
    global logger, window

    logger.log("Export helper exited!")

    # Close the window
    window.close()

    # Exit the programm
    sys.exit(0)


def show_error_popup(e):
    # Make the logger available locally
    global logger

    # Open a new window and hide it
    window = tk.Tk()
    window.withdraw()

    # Show a message error box
    messagebox.showerror("Error", e)

    # Close the helper
    close_helper()


if __name__ == '__main__':
    # Dataset variables
    available_datasets = []
    processed_datasets = []

    try:
        # Create the logger --> Write all logs into the log file folder -> export.log file
        logger = Logger("export.log")

        # Log when the helper was started
        logger.log("Export helper started!")

        # Validate settings
        settings_validator = SettingsValidator()
        logger.log("Starting settings validation...")
        settings_validator.validate()
        logger.log("Settings validation successful!")

        # Log current settings
        logger.log("Current settings:")
        for setting_name, setting_value in settings.items():
            logger.log(f'   {setting_name}: {setting_value}')

        # Create the dataset helper with the export input and output folders
        export_input_folder_path  = settings.get('export_input_folder_path')
        export_output_folder_path = settings.get('export_output_folder_path')
        dataset_helper = DatasetHelper(logger, export_input_folder_path, export_output_folder_path)

        # Create the gui of the helper and add what
        window = HelperWindow("Export helper")
        window.master.protocol("WM_DELETE_WINDOW", on_window_close)

        # Store the start time of the export
        start_time = datetime.datetime.now()

        # Create export daemon thread and start it.
        export_thread = threading.Thread(target=export)
        export_thread.daemon = True
        export_thread.start()

        # Open the gui
        window.open()
    except Exception as e:
        # Log the exception
        logger.log(f'{type(e).__name__}: {e}')
        # Show the error popup
        show_error_popup(e)