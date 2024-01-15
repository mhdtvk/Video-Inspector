#!/bin/bash

# Welcome
echo "Inspector Project"
echo -e "\nEnter the configuration setting: \n"

# Input folder path
while [ -z "$folder_path" ]; do
    
    echo -e "\n#[INFO]: Template: Sensor path: /home/mt/Public/1/0001/105917/color.kinect"
    echo -e "\n#[INFO]: The path you should enter : /home/mt/Public/1 "
    echo -e "\nFolder Path ? "
    read folder_path
done

# Input Json report path
echo -e "\nJson Report Path ? ( Press Enter for Default )"
read json_report_path

if [ -z "$json_report_path" ]; then
    json_report_path=$folder_path
fi

# Input Excel report path
echo -e "\nExcel Report Path ? ( Press Enter for Default )"
read excel_report_path

if [ -z "$excel_report_path" ]; then
    excel_report_path=$folder_path

fi

# Configuration Setting
echo -e " \nDefault configuration: 'Enable Report Generating' : True   'Light Mode' : True "
echo " For keeping default configuration just press 'Enter' "


# Input Enable Report Generating
echo -e "\nEnable Report Generating? (true/false)"
read enable_report

if [ -z "$enable_report" ]; then
    enable_report=true

elif [ "$enable_report" != true ] && [ "$enable_report" != false ]; then
    echo -e "\n# Error: Wrong Entry"
    read wait
    exit
fi

# Input Light Mode status
echo -e "\nLight Mode ? (true/false)"
read light_mode

if [ -z "$light_mode" ]; then
    light_mode=true

elif [ "$light_mode" != true ] && [ "$light_mode" != false ]; then
    echo -e "\n# Error: Wrong Entry"
    read wait
    exit

fi

# Loop to run the Inspector module multiple times

for name in "$folder_path"/*; do
    folder_name="/$(basename "$name")"
    python3 main_inspector.py -f "$folder_path$folder_name" -e $enable_report -j "${json_report_path}/json_report/${folder_name}" -l $light_mode -x "${excel_report_path}/excel_report/${folder_name}"
 done

echo -e "\n #[Info] The Json Report saved :\n ${excel_report_path}"
echo -e "\n #[Info] The Excel Report saved :\n ${json_report_path}"
read wait



