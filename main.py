
# test class
import re
from inspector import *

Root_path = r"C:\cv3_pr_20_10_2023_001"

for name in os.listdir(Root_path):
   if (name.isdigit() and len(name) == 6):
    Check_path = ( Root_path + '\\' + name)
    Report_name = 'Report_' + name
    Report_path = Root_path + '\\Inspector_Report\\' + Report_name

    # Calling the Inspector
    
    inspector = Inspector(path = Check_path, enable_report=True, json_path = Report_path)

    res = inspector.run() 

    if res == True:
     print("Folder Name : " + name + " \tResult : Check Successful ")
    else:
     print("Folder Name : " + name + " \tResult : Check Failed")

   elif(name != 'Inspector_Report'):  
     print("The path entered is in an unusual format")




