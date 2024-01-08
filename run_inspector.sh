#!/bin/bash

path='/media/mt/ibms_hd/CaVignal3/PatientRoom_Floor_-1/Oct_19_20_23_2023_EVS_recording_sessions'
# Loop to run the Inspector module multiple times

for name in "$path"/*; do
    folder_name="/$(basename "$name")"
    python3 main_inspector.py -f "$path$folder_name" -e True -j "/home/mt/Public/cv3_pr_20_10_2023_001/Inspector_Report/$folder_name" -l True -x "/home/mt/Public/cv3_pr_20_10_2023_001/excel_report/$folder_name"
 done