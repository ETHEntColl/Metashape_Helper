import os
import time
import tkinter as tk    

from .tkinter_helper import TkinterHelper

class HelperWindow():
    def __init__(self, title):
        # Helper
        self.tkinter_helper = TkinterHelper()

        # Create window
        self.master = tk.Tk()
        
        # Set the title & window size
        self.master.title(title)
        self.master.geometry("600x155")
        self.master.resizable(False, False)

        # Add the logo to the window
        logo = tk.PhotoImage(file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo.png'))
        self.master.wm_iconphoto(False, logo)
        
        # Make the content use the full width and height of the window
        self.master.grid_columnconfigure(0, weight=1)

        # Datasets done section
        self.datasets_done_progress_frame           = self.tkinter_helper.create_frame(self.master, 0, 0, [0], [1, 7, 1])
        self.datasets_done_progressbar_static_label = self.tkinter_helper.create_label(self.datasets_done_progress_frame, 0, 0, "Datasets done:", True, False)
        self.datasets_done_progressbar              = self.tkinter_helper.create_progressbar(self.datasets_done_progress_frame, 0, 1, False)
        self.datasets_done_amount_dynamic_label     = self.tkinter_helper.create_label(self.datasets_done_progress_frame, 0, 2, "0 of 0", False, False)

        # Current dataset section
        self.current_dataset_progress_label_frame          = self.tkinter_helper.create_label_frame(self.master, 1, 0, [0], [1, 7, 1], "Current Dataset:")
        self.current_dataset_name_static_label             = self.tkinter_helper.create_label(self.current_dataset_progress_label_frame, 0, 0, "Name:", True, True)
        self.current_dataset_name_dynamic_label            = self.tkinter_helper.create_label(self.current_dataset_progress_label_frame, 0, 1, "-", True, True)
        self.current_dataset_task_info_static_label        = self.tkinter_helper.create_label(self.current_dataset_progress_label_frame, 1, 0, "Task:", True, True)
        self.current_dataset_task_name_dynamic_label       = self.tkinter_helper.create_label(self.current_dataset_progress_label_frame, 1, 1, "-", True, True)
        self.current_dataset_task_number_dynamic_label     = self.tkinter_helper.create_label(self.current_dataset_progress_label_frame, 1, 2, "0 of 0", False, True)
        self.current_dataset_task_progressbar_static_label = self.tkinter_helper.create_label(self.current_dataset_progress_label_frame, 2, 0, "Task progress:", True, False)
        self.current_dataset_task_progressbar              = self.tkinter_helper.create_progressbar(self.current_dataset_progress_label_frame, 2, 1, False)
        self.current_dataset_task_dynamic_label            = self.tkinter_helper.create_label(self.current_dataset_progress_label_frame, 2, 2, "0 %", False, False)

        # Progressbar last update
        self.last_updated = time.monotonic()

    def update_datasets_done(self, step: float, processed_datasets: int, available_datasets: int):
        # Update the datasets done
        self.datasets_done_progressbar['value'] += step
        self.datasets_done_amount_dynamic_label.configure(text=f"{processed_datasets} of {available_datasets}")

    def update_task_info(self, task_name: str, current_task: int, task_amount: int):
        # Update the current task name and qnumber
        self.current_dataset_task_name_dynamic_label.configure(text=task_name)
        self.current_dataset_task_number_dynamic_label.configure(text=f"{current_task} of {task_amount}")

    def throttle(func):
        """
        A decorator that throttles a function to run at most once per second.
        """
        last_called = 0
        def throttled(*args, **kwargs):
            nonlocal last_called
            elapsed = time.time() - last_called
            if elapsed > 1:
                last_called = time.time()
                return func(*args, **kwargs)
        return throttled

    @throttle
    def update_current_dataset_task_progress(self, value: float):
        # Update the current task progressbar and percentage
        self.current_dataset_task_progressbar['value'] = value
        percentage = self.current_dataset_task_progressbar['value']
        self.current_dataset_task_dynamic_label.configure(text=f"{int(percentage)} %")

    def reset_current_dataset_task_progressbar(self):
        # Reset the current task progressbar and percentage
        self.current_dataset_task_progressbar['value'] = 0
        percentage = self.current_dataset_task_progressbar['value']
        self.current_dataset_task_dynamic_label.configure(text=f"{int(percentage)} %")
    

    def open(self):
        # Open the window
        self.master.mainloop()


    def close(self):
        # Close the window
        self.master.quit()