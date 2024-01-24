#!/usr/bin/env python3
## @defgroup inspector_project_gui inspector_project_gui.py
#@{

import tkinter as tk
from tkinter import filedialog
import subprocess
import os

def run_inspector():
    """
    @brief Run the Inspector module multiple times.

    This function retrieves folder path, JSON report path, Excel report path,
    enable report flag, and light mode flag from the GUI, and runs the Inspector
    module using the provided parameters.
    """
    folder_path = folder_path_entry.get()
    json_report_path = json_report_path_entry.get()
    excel_report_path = excel_report_path_entry.get()
    enable_report = enable_report_var.get()
    light_mode = light_mode_var.get()

    # Loop to run the Inspector module multiple times
    for name in os.listdir(folder_path):
        folder_name = "/" + name
        subprocess.run([
            'python3' if os.name == 'posix' else 'python',
            os.path.join(os.path.dirname(__file__), 'arg_parser.py'),
            '-f', f'{folder_path}{folder_name}',
            '-e', str(enable_report),
            '-j', f'{json_report_path}/json_report/{folder_name}',
            '-l', str(light_mode),
            '-x', f'{excel_report_path}/excel_report/{folder_name}'
        ])

    result_label.config(text="Inspector has finished running.")

def open_json_directory():
    """
    @brief Open the JSON report directory using the default system file manager.

    This function retrieves the JSON report path from the GUI and opens the
    directory in the default system file manager.
    """
    json_report_path = json_report_path_entry.get()
    subprocess.run(['xdg-open' if os.name == 'posix' else 'start', json_report_path])

def open_excel_directory():
    """
    @brief Open the Excel report directory using the default system file manager.

    This function retrieves the Excel report path from the GUI and opens the
    directory in the default system file manager.
    """
    excel_report_path = excel_report_path_entry.get()
    subprocess.run(['xdg-open' if os.name == 'posix' else 'start', excel_report_path])

def show_help_popup():
    """
    @brief Show a help popup window.

    This function creates a popup window with template information.
    """
    popup_window = tk.Toplevel(app)
    popup_window.title("Hint")

    folder_path_guide_popup = tk.Label(popup_window, text="Template: Sensor path: /home/mt/Public/1/0001/105917/color.kinect\nThe path you should enter : /home/mt/Public/1", wraplength=300, justify="left", font=("Arial", 8))
    folder_path_guide_popup.pack(padx=10, pady=10)

# Create the main application window
app = tk.Tk()
app.title("Inspector GUI")

# Input folder path
folder_path_label = tk.Label(app, text="Folder Path:")
folder_path_label.grid(row=0, column=0, pady=5)  # Remove columnspan

folder_path_entry = tk.Entry(app)
folder_path_entry.grid(row=0, column=1, pady=5)  # Adjust row number

# Help button to show the help information in a pop-up window
help_button = tk.Button(app, text="Hint", command=show_help_popup)
help_button.grid(row=0, column=2, pady=5)


# Input Json report path
json_report_path_label = tk.Label(app, text="Json Report Path:")
json_report_path_label.grid(row=2, column=0)
json_report_path_entry = tk.Entry(app)
json_report_path_entry.grid(row=2, column=1)

# Input Excel report path
excel_report_path_label = tk.Label(app, text="Excel Report Path:")
excel_report_path_label.grid(row=3, column=0)
excel_report_path_entry = tk.Entry(app)
excel_report_path_entry.grid(row=3, column=1)

# Configuration Setting
enable_report_var = tk.BooleanVar()
enable_report_checkbutton = tk.Checkbutton(app, text="Enable Report Generating", variable=enable_report_var)
enable_report_checkbutton.grid(row=4, column=0)

light_mode_var = tk.BooleanVar()
light_mode_checkbutton = tk.Checkbutton(app, text="Light Mode", variable=light_mode_var)
light_mode_checkbutton.grid(row=4, column=1)

# Run Inspector button
run_inspector_button = tk.Button(app, text="Run Inspector", command=run_inspector)
run_inspector_button.grid(row=5, column=0, columnspan=2, pady=10)

# Open JSON report directory button
open_json_directory_button = tk.Button(app, text="Open JSON Report Directory", command=open_json_directory)
open_json_directory_button.grid(row=6, column=0, columnspan=2, pady=10)

# Open Excel report directory button
open_excel_directory_button = tk.Button(app, text="Open Excel Report Directory", command=open_excel_directory)
open_excel_directory_button.grid(row=7, column=0, columnspan=2, pady=10)

# Result label
result_label = tk.Label(app, text="")
result_label.grid(row=8, column=0, columnspan=2)

# Run the Tkinter event loop
app.mainloop()

# @} ##
