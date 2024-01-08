from typing import Any
import numpy as np
from os import walk
import json
import time
from tqdm import tqdm
import os
# Import checkers class
from Checker import *
from Excel_generator2 import *

# The Class for preparing the Report and Export it in Json Format        
class ReportGen():
    def __init__(self, json_path: str , check_report_struct: dict , ret: bool ,check_path  ):
        self.json_path = json_path
        self.check_path =  check_path
        self.check_report = check_report_struct
        self.final_report = {}
        self.time = Time_generator()
        self.overall_data = {}
        self.result = ret
        

    def run(self):
        self.report_detail_generate()
        self.final_report["Report Details"] = self.overall_data
        self.final_report["Checks"] = self.check_report
        # parsing the class check_report_struct
        with open(self.json_path , 'w') as file:
         json.dump(self.final_report, file, indent=2)

    def report_detail_generate(self):
        ret = True
        self.overall_data['Report Name'] = 'Report' + self.time
        self.overall_data['Timestamp'] = self.time
        self.overall_data['Input_folder'] = self.check_path
        self.overall_data['Result'] = self.result


# Preparing Recent Time
def Time_generator():
        nowtime = time.localtime() 
        time_str=str(nowtime.tm_mon)+'-'+str(nowtime.tm_mday)+'-'+str(nowtime.tm_year)+"_"+str(nowtime.tm_hour)+'_'+str(nowtime.tm_min)+'_'+str(nowtime.tm_sec)
        
        return time_str


class Inspector():
    def __init__(self, path: str = "mypath", enable_report: bool = True, json_path:str = "my_json_file" , Light_mode = True):
        self.path = path
        self.json_path = json_path
        self.enable_report = enable_report
        self.json_report = {}
        self.result = None
        self.Light_mode = Light_mode
        self.Excel_report = {}
        

    def run(self):

            # perfom check
        
            checker = Checker(self.path, self.Light_mode )
            self.result,self.json_report, self.Excel_report = checker.run()

            if self.enable_report == True:
             # create the report
             report_generator = ReportGen(self.json_path , self.json_report, self.result , self.path)
             report_generator.run()
    

            return self.result ,self.Excel_report
    

# The Main
class Inspector_call: 
    def __init__(self, root_path: str = '', enable_report: bool = True , json_path:str = ' ',  Light_mode = True , excel_path=''):
        self.root_path = root_path
        self.result = []
        self.excel_gen = {}
        self.json_report = json_path
        self.excel_path = excel_path
        self.Light_mode = Light_mode



    def run(self):
      folder_name = os.path.basename(self.root_path)
      self.excel_gen = Excel_generator(self.excel_path + f"{folder_name}_Excel_Report.xlsx")


      if not os.path.exists(self.json_report):
        os.makedirs(self.json_report)

      for name in tqdm(os.listdir(self.root_path)) :
        if (name.isdigit() and len(name) == 6):

          Check_path = ( self.root_path + '/' + name)
          Report_name = 'Report_' + name
          Report_path = self.json_report + Report_name

          # Calling the Inspector

          inspector = Inspector(path = Check_path, enable_report=True, json_path = Report_path, Light_mode = self.Light_mode)

          res , tmp_dic_report = inspector.run() 

          if res == True:
            self.result.append("Folder Name : " + name + " \tCheck : Successful ")
            self.excel_gen.run(tmp_dic_report,name)
          else:
            self.result.append("Folder Name : " + name + " \tCheck : Failed")
            self.excel_gen.run(tmp_dic_report,name)  

        elif(name != 'Inspector_Report' and name != 'Excel_Report.xlsx'):  
            print(f"The path has an unusual folder or file: {name}")
      self.excel_gen.Create_Summary_Sheet()

      for one_report in self.result:
        print(one_report)



