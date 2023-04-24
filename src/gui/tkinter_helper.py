from tkinter import ttk
import tkinter as tk

class TkinterHelper:
    def __init__(self):
        pass

    def create_frame(self, window, row, column, row_weights, column_weights):
        frame = tk.Frame(window)
        frame.grid(row=row, column=column, padx=10, pady=(10, 0), sticky="wens")
        for row_index in range(len(row_weights)):
            frame.grid_rowconfigure(row_index, weight=row_weights[row_index])
        for col_index in range(len(column_weights)):
            frame.grid_columnconfigure(col_index, weight=column_weights[col_index])
        return frame
    
    def create_label_frame(self, window, row, column, row_weights, column_weights, text):
        frame = tk.LabelFrame(window, text=text, padx=5, pady=5)
        frame.grid(row=row, column=column, padx=10, pady=(10, 0), sticky="wens")
        for row_index in range(len(row_weights)):
            frame.grid_rowconfigure(row_index, weight=row_weights[row_index])
        for col_index in range(len(column_weights)):
            frame.grid_columnconfigure(col_index, weight=column_weights[col_index])
        return frame

    def create_label(self, window, row, column, text, align_left, padding_bottom):
        if align_left:
            label = tk.Label(window, text=text, anchor="w")
        else:
            label = tk.Label(window, text=text, anchor="center")
        if padding_bottom:
            label.grid(row=row, column=column, pady=(0, 5), sticky='wens')
        else:
            label.grid(row=row, column=column, sticky='wens')
        return label
    
    def create_button(self, window, row, column, text, command, padding_left):
        button = tk.Button(window, text=text, command=command)
        if padding_left:
            button.grid(row=row, column=column, padx=(5, 0), sticky='wens')
        else:
            button.grid(row=row, column=column, sticky='wens')
        return button

    def create_progressbar(self, window, row, column, padding_bottom):
        progressbar = ttk.Progressbar(window, orient='horizontal', mode='determinate')
        if padding_bottom:
            progressbar.grid(row=row, column=column, pady=(0, 5), sticky='wens')
        else:
            progressbar.grid(row=row, column=column, sticky='wens')
        return progressbar

    
