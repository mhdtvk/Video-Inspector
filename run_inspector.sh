#!/bin/bash

# Input folder path
echo "Folder Path : "
read folder_path

# Use the default value if the user has not entered a value.
if [ -z "$folder_path" ]; then
    '/home/mt/Public/1'

# Input Json report path
echo " Json Report Path : "
read json_report_path

if [ -z "$json_report_path" ]; then
    '/home/mt/Public/1/cv3_pr_20_10_2023_001'

# Input Excel report path
echo " Excel Report Path : "
read excel_report_path

if [ -z "$excel_report_path" ]; then
    '/home/mt/Public/1/cv3_pr_20_10_2023_001'




# Loop to run the Inspector module multiple times

for name in "$folder_path"/*; do
    folder_name="/$(basename "$name")"
    python3 main_inspector.py -f "$folder_path$folder_name" -e True -j "${json_report_path}/json_report/${folder_name}" -l True -x "${excel_report_path}/excel_report/${folder_name}"
 done