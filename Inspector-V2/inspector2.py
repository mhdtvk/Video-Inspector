from typing import Any
import numpy as np
import os
import json
from os import walk
import time
# Import checkers class
import Light_Checker as LChk
import Detailed_Checker  as Dchk


# The Main Class     
class Inspector():
    def __init__(self, path: str = "mypath", enable_report: bool = True, json_path:str = "my_json_file" , Light_mode = True):
        self.path = path
        self.json_path = json_path
        self.enable_report = enable_report
        self.report=''
        self.result = None
        self.failed_check = ''
        self.Light_mode = Light_mode
        self.Excel_report = {}

    def run(self) -> bool:

            # perfom check
        if self.Light_mode :
            checker = LChk.Checker()
            self.result,self.report, self.Excel_report = checker.run(self.path)

            if self.enable_report == True:
             # create the report
             report_gen = LChk.ReportGen(self.json_path , self.report , self.result , self.path )
             report_gen.run()
        else:
            checker = Dchk.Checker()
            self.result,self.report , self.failed_check = checker.run(self.path)
            if self.enable_report == True:
             # create the report
             report_gen = Dchk.ReportGen(self.json_path , self.report , self.result , self.path ,self.failed_check)
             report_gen.run()
        

        return self.result , self.Excel_report
