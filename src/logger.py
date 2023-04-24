from datetime import timedelta
import logging
import os
import time

from settings.settings import settings
from settings.settings_exceptions import SettingNotFoundError

class Logger:
    def __init__(self, filename: str):
        # Check if the logfile path exists in settings
        log_output_folder_path = settings.get('log_output_folder_path')
        if log_output_folder_path is None:
            raise SettingNotFoundError("Log output folder path not set!")
        if not os.path.isdir(log_output_folder_path):
            raise FileNotFoundError(f"The log file folder '{log_output_folder_path}' does not exist")
        
        # Set up the log file path
        logfile = os.path.join(log_output_folder_path, filename)

        # Delete existing log file
        if os.path.isfile(logfile):
            os.remove(logfile)

        # Create the new log file
        os.makedirs(os.path.dirname(logfile), exist_ok=True)

        # Set up the logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Set up a logger file handler
        file_handler = logging.FileHandler(logfile)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Add a logger handler
        self.logger.addHandler(file_handler)

    def log(self, message):
        self.logger.info(message)

    def log_task_start(self, task_name: str):
        # Log the task name
        self.log(f"   Start task: {task_name}")

    def log_task_finish(self, start_time: float):
        # Get the elapsed time and log it
        elapsed_time_string = self.get_elapsed_time_string(start_time)
        self.log(f"      Finished Task! Elapsed time: {elapsed_time_string}")

    def get_elapsed_time_string(self, start_time: float):
        # Get the current time
        end_time = time.time()

        # Calculate the elapsed time and format it
        elapsed_time = end_time - start_time
        elapsed_time_string = str(timedelta(seconds=elapsed_time))
        
        # Return the formatted elapsed time
        return elapsed_time_string