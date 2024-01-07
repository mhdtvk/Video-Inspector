
# test class
import re
from tqdm import tqdm
from inspector2 import *
from Excel_generator2 import *

Root_path = r"C:\cv3_pr_20_10_2023_001"

result = []
tmp_Excel_report = {}
excel_gen = Excel_generator()

for name in tqdm(os.listdir(Root_path)) :
  if (name.isdigit() and len(name) == 6):
    Check_path = ( Root_path + '\\' + name)
    Report_name = 'Report_' + name
    Report_path = Root_path + '\\Inspector_Report\\' + Report_name

    # Calling the Inspector

    inspector = Inspector(path = Check_path, enable_report=True, json_path = Report_path, Light_mode = False )

    res , tmp_dic_report = inspector.run() 

    if res == True:
      result.append("Folder Name : " + name + " \tCheck : Successful ")
      excel_gen.combine(tmp_dic_report,name)
    else:
      result.append("Folder Name : " + name + " \tCheck : Failed")
      excel_gen.combine(tmp_dic_report,name)  

  elif(name != 'Inspector_Report'):  
      print("The path entered is in an unusual format")

excel_gen.run()
for one_report in result:
  print(one_report)




