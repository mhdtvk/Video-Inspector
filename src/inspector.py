from typing import Any
import numpy as np
import os
import json
from os import walk
import time

def Time_generator():
        nowtime = time.localtime() 
        time_str=str(nowtime.tm_mon)+'-'+str(nowtime.tm_mday)+'-'+str(nowtime.tm_year)+"_"+str(nowtime.tm_hour)+'_'+str(nowtime.tm_min)+'_'+str(nowtime.tm_sec)
        
        return time_str

class DataManager():

    def __init__(self, path: str = "mypath"):
        self.path = path
        self.file_number = None
        self.time = ''
        self.raw_data = {}
        self.txt_data = []
        self.meta_data = []
        self.combined_data={}
        self.check_result = True

    def calc_num_file(self) -> int:
        num_meta_found_files=0
        for name in os.listdir(self.path):
            if (name.lower().endswith(('.meta'))):
                num_meta_found_files +=1
        return num_meta_found_files

    def read(self) -> bool:
        ret = True
        self.file_number=self.calc_num_file()
        if(self._read_raw_data() == False):
            ret = False

        if(self._read_txt_data() == False):
            ret = False

        if(self._read_metadata() == False):
            ret = False       

        if(self.data_combiner() == False):
            ret= False

        return ret

    def _read_raw_data(self):
        ret = True

        # read self.path 

        return ret

    def _read_txt_data(self):
        ret = True
        for name in os.listdir(self.path):
            if (name.lower().endswith(('.txt'))):
        # read self.path
                data = []
                with open(self.path+'\\'+name, "r") as file:
                 for line in file:
              # Split each line into two columns and convert them to integers.
                    columns = line.strip().split(' ')
                    row = [int(col) for col in columns]
                    data.append(row)
                file.close()
                self.txt_data.append(np.array(data))
        
        if self.txt_data== []:
            ret==False

        return ret

    def _read_metadata(self):
        ret = True

        # read self.path
        for name in os.listdir(self.path):
            if (name.lower().endswith(('.meta'))):
        # read self.path
                data = {}
                with open(self.path+'\\'+name, "r") as file:
                 for line in file:
              # Split each line into two columns and convert them to integers.
              # Change the delimiter (e.g., ',' or '\t') if needed.
                    columns = line.strip().split(' ')
                    data[columns[0]]=columns[1]
                file.close()
                self.meta_data.append(data)
        
             
        if (self.meta_data==[]):
            ret=False

        return ret

    def data_combiner(self)->bool:
        ret=True

        self.combined_data['meta']=self.meta_data
        self.combined_data['txt']=self.txt_data
        self.combined_data['raw']=self.raw_data
        self.combined_data['path']= self.path

        if (self.combined_data=={}):
            ret=False

        return ret

    def get_data(self) :
        return self.combined_data


class Check:
    def __init__(self, data : dict):
        self.meta_data = data["meta"]
        self.txt_data = np.array(data["txt"])
        self.raw_data = data["raw"]
        self.path = data["path"]
        self.code = None
        self.description = None
        self.result = True
        self.report={}

    def serialize(self):
        self.report=self.report|{'code':self.code,"description":self.description,"Result":self.result}
        return self.report

class NumberOfFilesCheck(Check):
    def __init__(self,data: dict):
        super().__init__(data)
        self.code = "00101"
        self.description = " Check number of files"
        self.num_found_file = 0
        self.num_exp_file = 0
        self.num_raw_exp_files = 0
        self.num_raw_found_files = 0
        self.num_meta_exp_files = 0
        self.num_meta_found_files = 0
        self.num_txt_exp_files = 0
        self.num_txt_found_files = 0
        

    def run(self) -> bool:
        ret = True

        # Checking the overall number of files inside each sensor's folders
        self.num_file_found=(len(os.listdir(self.path))) 
        
        self.num_exp_file= (3*int((self.meta_data[0]["file"])[2])) 
        
        if self.num_file_found != self.num_exp_file:
            ret = False

        # read meta file and get the information of 2nd row "file N/M" , the M value ( for raw)
        self.num_raw_exp_files = int((self.meta_data[0]["file"])[2])
        #  check if number of rawv/rawa files is equal to num_raw_exp_files
        for name in os.listdir(self.path):
            if (name.lower().endswith(('.rawv','.rawa'))):
                self.num_raw_found_files +=1
                

        if not(self.num_raw_exp_files == self.num_raw_found_files):
            ret = False
        # read meta file and get the information of the number of files ( for meta)
        self.num_meta_exp_files = int((self.meta_data[0]["file"])[2])

        #  check if number of meta files is equal to num_meta_exp_files
        for name in os.listdir(self.path):
            if (name.lower().endswith(('.meta'))):
                self.num_meta_found_files +=1

        if self.num_meta_exp_files != self.num_meta_found_files:
            ret = False
        # read meta file and get the information of the number of files ( for txt)
        self.num_txt_exp_files = int((self.meta_data[0]["file"])[2])

        #  check if number of txt files is equal to num_txt_exp_files
        for name in os.listdir(self.path):
            if (name.lower().endswith(('.txt'))):
                self.num_txt_found_files +=1

        if self.num_txt_exp_files != self.num_txt_found_files:
            ret = False

        self.result = ret
        return self.result

    def serialize(self):
        super().serialize()
        self.report=self.report|{
            "num_exp_file" : self.num_exp_file,
            "num_file_found":self.num_file_found,
            "num_raw_exp_files":self.num_raw_exp_files,
            "num_raw_found_files":self.num_raw_found_files,
            "num_meta_exp_files":self.num_meta_exp_files,
            "num_meta_found_files":self.num_meta_found_files,
            "num_txt_exp_files":self.num_txt_exp_files,
            "num_txt_found_files":self.num_txt_found_files}
        return self.report
        
        

class UnexpectedFileCheck(Check):
     def __init__(self,data):
         super().__init__(data)
         self.code = "00102"
         self.description = " Check type of files"
         self.num_unexp_file = 0
         self.unexp_file= ''


     def run(self):
         for name in os.listdir(self.path):
             if not(name.lower().endswith(('.meta', '.rawv','.rawa', '.txt'))):
              self.num_unexp_file += 1
              self.unexp_file += name
         if(self.num_unexp_file>0):
             self.result = False
         
         return self.result

     def serialize(self):
         super().serialize()
         self.report=self.report|{'num_unexp_file':self.num_unexp_file ,
                                   'unexp_file' : self.unexp_file }
         return self.report

class Sizecheck(Check):
    def __init__(self, data) -> Any:
        super().__init__(data)
        self.code = "00201"
        self.description = " Check size of files"
        self.zero_size_file= ''

    def run(self):
        w = walk(self.path)
        for (dirpath, dirnames, filenames) in w:
            for file in filenames: 
                file_size = os.path.getsize(dirpath+"\\"+file)
                if file_size==0:
                 self.result = False
                 self.zero_size_file += file
        return self.result
    
    def serialize(self):
         super().serialize()
         self.report=self.report|{'zero_size_file':self.zero_size_file }
         return self.report

class RawSizeCheck(Check):
    def __init__(self, data: dict):
        super().__init__(data)
        self.code = "00202"
        self.description = " Check size of raw files"
        self.raw_unexp_name = ''

    
    def run(self):
        calc_size=(np.sum(self.txt_data[:,1]))
        w = walk(self.path)
        for (dirpath, dirnames, filenames) in w:
            for file in filenames: 
                if file.lower().endswith(('.rawv','.rawa')):
                    real_size = os.path.getsize(dirpath+"\\"+file)
                    if not(calc_size==real_size):
                        self.result = False
                        self.raw_unexp_name += file

        return self.result
    
    def serialize(self):
         super().serialize()
         self.report=self.report|{'raw_unexp_name':self.raw_unexp_name }
         return self.report
    
#class AbnormalFrameDurationCheck(Check):
#     def __init__(self, code: int, descriptionì:str="", th: int = 2):
#         super().__init__(code=code
#         self.th = th
#
#     def serialize(self):
#         super().serialize()

#     def run(self, data) -> bool
#         ret = True
#         self.exp_avg_frame_duration = self._compute_exp_avg_frame_duration(data)
#         # perform the check....

#         if number of abnormal_frame_duration > th):
#             ret = False

#         return ret
    
#     def _compute_exp_avg_frame_duration(self, ):
#         return 


class Checker():
    def __init__(self):
        self.data = []
        self.report={}
    def run(self,data:{}):
        result = True
        self.data=data
        # init the struct
        check_report_struct = []

        # check for folder contents
        nf_check = NumberOfFilesCheck(data)
        
        if nf_check.run() == False:
            result = False
        self.report['NumberOfFilesCheck']=nf_check.serialize() 

        tf_check = UnexpectedFileCheck(data)
        if tf_check.run() == False:
            result = False
        self.report['UnexpectedFileCheck']= tf_check.serialize()

        siz_check= Sizecheck(data)
        if siz_check.run() == False:
            result = False
        self.report['sizecheck']=siz_check.serialize()

        RawSize_check = RawSizeCheck(data)
        if RawSize_check.run() == False:
            result = False
        self.report['RawSizeCheck']=RawSize_check.serialize()
 


        #check_report_struct.append(cnf_check.serialize())
        return result, self.report
        
       
        
class ReportGen():
    def __init__(self, json_fn: str , check_report_struct: dict , ret: bool , path):
        self.path = path
        self.json_fn = json_fn
        self.ceck_report = check_report_struct
        self.final_report = {}
        self.time = Time_generator()
        self.overall_data = {}
        self.result = ret

    def run(self):
        self.report_detail_generate()
        self.final_report["Report Details"] = self.overall_data
        self.final_report["Checks"] = self.ceck_report
        # parsing the class check_report_struct
        with open(self.json_fn, 'w') as file:
         json.dump(self.final_report, file, indent=4)

    def report_detail_generate(self):
        ret = True
        self.overall_data['Report Name'] = 'Report' + self.time
        self.overall_data['Timestamp'] = self.time
        self.overall_data['Input_folder'] = self.path
        self.overall_data['Result'] = self.result

        
class Inspector():
    def __init__(self, path: str = "mypath", enable_report: bool = True, json_fn:str = "my_json_file"):
        self.path = path
        self.json_fn = json_fn
        self.enable_report = enable_report
        self.report=''

    def run(self) -> bool:

        # read Data
        data_manager = DataManager(self.path)
        if(data_manager.read() == True):

            # perfom check
            checker = Checker()
            ret,self.report= checker.run(data_manager.get_data())
            
        if self.enable_report == True:
            # create the report
            report_gen = ReportGen(self.json_fn,self.report,ret , (data_manager.get_data())['path'])
            report_gen.run()

        
        return ret
