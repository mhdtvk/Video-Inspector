
try:
    from typing import Any
    from os import walk
    import json
    import time
    from tqdm import tqdm
    import os
except ImportError as e:
    print(f"Error: {e}")
    exit(1)

# Import checkers class
from check_levels import *
from excel_generator import *

class ReportGenerator():
    def __init__(self, json_path: str, check_report_struct: dict, ret: bool, check_path):
        self.json_path = json_path
        self.check_path = check_path
        self.check_report = check_report_struct
        self.final_report = {}
        self.time = time_generator()
        self.overall_data = {}
        self.result = ret
        

    def run(self):
        self.report_detail_generate()
        self.final_report["Report Details"] = self.overall_data
        self.final_report["Checks"] = self.check_report
        # Parsing the class check_report_struct
        with open(self.json_path, 'w') as file:
            json.dump(self.final_report, file, indent=2)

    def report_detail_generate(self):
        ret = True
        self.overall_data['Report Name'] = 'Report' + self.time
        self.overall_data['Timestamp'] = self.time
        self.overall_data['Input_folder'] = self.check_path
        self.overall_data['Result'] = self.result


# Preparing Recent Time
def time_generator():
    nowtime = time.localtime()
    time_str = (
        str(nowtime.tm_mon)
        + "-"
        + str(nowtime.tm_mday)
        + "-"
        + str(nowtime.tm_year)
        + "_"
        + str(nowtime.tm_hour)
        + "_"
        + str(nowtime.tm_min)
        + "_"
        + str(nowtime.tm_sec)
    )
    
    return time_str


class Inspector():
    def __init__(self, root_path: str = '', enable_report = False, json_path: str = '', light_mode=True, excel_path=''):
        self.root_path = root_path

        self.enable_json_report = enable_report
        self.light_mode = light_mode
        self.json_report_path = json_path
        self.json_report_file = {}

        self.excel_report_path = excel_path

        self.boolean_result = None

        self.print_in_terminal_result = []

    def run(self):
        # perform check
        basename = os.path.basename(self.root_path)
        if (basename).isdigit() and len(basename) == 4:
            excel_report_generator = ExcelGenerator(self.excel_report_path )

            try:
                if not os.path.exists(self.json_report_path):
                  os.makedirs(self.json_report_path)
            except PermissionError :
                print(" You don't have permission to export reports to the enterd path")

            for folders_name in tqdm(os.listdir(self.root_path)):
                if folders_name.isdigit() and len(folders_name) == 6:
                    check_path = (self.root_path + '/' + folders_name)
                    report_name = '/Report_' + folders_name
                    json_report_path = self.json_report_path + report_name

                    checker = Checker(check_path, self.light_mode)
                    self.boolean_result, self.json_report_file, tmp_excel_report = checker.run()

                    if self.enable_json_report != 'false':
                       # create the report
                      report_generator = ReportGenerator(json_report_path, self.json_report_file, self.boolean_result, check_path)
                      report_generator.run()

                    if self.boolean_result:
                        self.print_in_terminal_result.append(f"Folder Name: {folders_name}\tCheck: Failed")
                        excel_report_generator.run(tmp_excel_report, folders_name)
                    else:
                        self.print_in_terminal_result.append(f"Folder Name: {folders_name}\tCheck: Failed")
                        excel_report_generator.run(tmp_excel_report, folders_name)
                elif folders_name not in ['json_report', 'excel_report']:
                    print(f"# Warning : The Folder has an unusual folder or file: {folders_name}")

            excel_report_generator.rearrange_critical_rows()
            excel_report_generator.design_excel()
            excel_report_generator.create_summary_sheet()



            # Providing output for showing in terminal
            print(f"\nChecked route: {self.root_path}\n")
            for one_report in self.print_in_terminal_result:
                print(one_report)
        else:
            print(f"\n# Warning: The path has an unusual folder or file:\n {self.root_path}")







