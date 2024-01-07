from typing import Any
import numpy as np
import os
from os import walk
import json
import time


# Preparing Recent Time
def Time_generator():
        nowtime = time.localtime() 
        time_str=str(nowtime.tm_mon)+'-'+str(nowtime.tm_mday)+'-'+str(nowtime.tm_year)+"_"+str(nowtime.tm_hour)+'_'+str(nowtime.tm_min)+'_'+str(nowtime.tm_sec)
        
        return time_str

# Defining ou function that can find the Folders with Zero Size
def get_folderAndfile_sizes(root_folder):
    folder_sizes = {}
    for item in os.listdir(root_folder):
        item_path = os.path.join(root_folder, item)
        if os.path.isdir(item_path):
            folder_sizes[item] = sum(os.path.getsize(os.path.join(item_path, f)) for f in os.listdir(item_path))
        else:
            folder_sizes[item] = os.path.getsize(item_path)
    return folder_sizes

# Importing Data from our Data set and Preparing it for using in our Checks
class DataManager():

    def __init__(self, path: str = "mypath"):
        self.path = path
        self.time = ''
        self.data = {}
        self.check_result = True


    def read(self) -> bool:
        ret = True

        if(self._read_raw_data() == False):
            ret = False

        if(self._read_txt_data() == False):
            ret = False

        if(self._read_metadata() == False):
            ret = False   

        return ret


    def _read_raw_data(self):
        ret = True
        for file_name in os.listdir(self.path):
            file_base_name, file_extension = os.path.splitext(file_name)
            if ( file_extension == '.rawv' or file_extension == '.rawa'):
        # read self.path
                data = []
                self.data[file_base_name] = {'rawa':(data) }
                self.data[file_base_name]['rawv'] = (data) 

                if (self.data[file_base_name]['rawv'] == {} and self.data[file_base_name]['rawa'] == {}):
                    ret==False
        # read self.path 
        return ret

    def _read_txt_data(self):
        ret = True
        for file_name in os.listdir(self.path):
            file_base_name, file_extension = os.path.splitext(file_name)
            if ( file_extension == '.txt'):
        # read self.path
                data = []
                with open(self.path+'\\'+file_name, "r") as file:
                 for line in file:
              # Split each line into two columns and convert them to integers.
                    columns = line.strip().split(' ')
                    row = [int(col) for col in columns]
                    data.append(row)
                file.close()
                self.data[file_base_name]['txt'] = (data) 

        if self.data== {}:
            ret==False

        return ret

    def _read_metadata(self):
        ret = True

        # read self.path
        for file_name in os.listdir(self.path):
            file_base_name, file_extension = os.path.splitext(file_name)
            if ( file_extension == '.meta'):
        # read self.path
                data = {}
                with open(self.path+'\\'+file_name, "r") as file:
                 for line in file:
              # Split each line into two columns and convert them to integers.
              # Change the delimiter (e.g., ',' or '\t') if needed.
                    columns = line.strip().split(' ')
                    data[columns[0]]=columns[1]
                file.close()
                
                self.data[file_base_name]['meta'] = data


             
        if (self.data=={}):
            ret=False

        return ret


    def get_data(self) :
        return self.data

# The Parent Class for each level of Checking
class Check:
    def __init__(self, data : dict , path : str):
        self.path = path
        self.code = None
        self.description = None
        self.result = True
        self.report={}

    def serialize(self):
        self.report=self.report|{'code':self.code,"description":self.description,"Result":self.result}
        return self.report
    

# Class for Root checking
class AbnormalFolderInRootCheck(Check):
    def __init__(self, data: dict, path: str):
        super().__init__(data, path)
        self.code = "00001"
        self.description = " Checking the Root Folder for abnormal Files or Folders"
        self.num_unexp_file = 0
        self.unexp_file = ' '


    def run( self ) -> bool:
        for name in os.listdir(self.path):
             if not(name.lower() == ('audio.kinect') or name.lower() ==('color.kinect') or name.lower() ==('depth.kinect') or name.lower() ==('ir.kinect') or name.lower() == ('audio.i2smems') or name.lower() ==('depth.flexx2') or name.lower() ==('ir.flexx2') or name.lower() ==('thermal.lepton')):
              self.num_unexp_file += 1 
              self.unexp_file += (name + ' , ' )

        if(self.num_unexp_file > 0):
         self.result = False
         
        return self.result
    
    def serialize(self):
         super().serialize()
         self.report=self.report|{'num_unexp_file':self.num_unexp_file ,
                                   'unexp_file' : self.unexp_file }
         return self.report


class EmptyFileInRootCheck(Check):
    def __init__(self, data: dict, path: str):
        super().__init__(data, path)
        self.code = "00002"
        self.description = " Checking the Root Folder for abnormal Folder Size"
        self.zero_size_folder = ' '


    def run( self ) -> bool:
        sizes = get_folderAndfile_sizes(self.path)
        for name in sizes:
            if sizes[name] == 0:
                self.result = False
                self.zero_size_folder += (name + ' , ')
        return self.result
    
    def serialize(self):
         super().serialize()
         self.report=self.report|{'zero_size_folder':self.zero_size_folder }
         return self.report

# Class for Sensors checking
class NumberOfFilesCheck(Check):
    def __init__(self,data: dict , path : str):
        super().__init__(data,path)
        self.meta_data = data['00000000']['meta']
        
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
        # Checking the overall number of files inside each sensor's folders
        self.num_file_found=(len(os.listdir(self.path))) 
        self.num_exp_file= (3*int((self.meta_data["file"])[2])) 
        
        if self.num_file_found != self.num_exp_file:
            self.result = False

        # read meta file and get the information of 2nd row "file N/M" , the M value ( for raw)
        self.num_raw_exp_files = int((self.meta_data["file"])[2])
        #  check if number of rawv/rawa files is equal to num_raw_exp_files
        for name in os.listdir(self.path):
            if (name.lower().endswith(('.rawv','.rawa'))):
                self.num_raw_found_files += 1
                

        if not(self.num_raw_exp_files == self.num_raw_found_files):
            self.result = False
        # read meta file and get the information of the number of files ( for meta)
        self.num_meta_exp_files = int((self.meta_data["file"])[2])

        #  check if number of meta files is equal to num_meta_exp_files
        for name in os.listdir(self.path):
            if (name.lower().endswith(('.meta'))):
                self.num_meta_found_files += 1

        if self.num_meta_exp_files != self.num_meta_found_files:
            self.result = False
        # read meta file and get the information of the number of files ( for txt)
        self.num_txt_exp_files = int((self.meta_data["file"])[2])

        #  check if number of txt files is equal to num_txt_exp_files
        for name in os.listdir(self.path):
            if (name.lower().endswith(('.txt'))):
                self.num_txt_found_files +=1

        if self.num_txt_exp_files != self.num_txt_found_files:
            self.result = False

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
     def __init__(self,data , path : str):
         super().__init__(data,path)

         self.code = "00102"
         self.description = " Check type of files"
         self.num_unexp_file = 0
         self.unexp_file= ''


     def run(self):
         for name in os.listdir(self.path):
             if not(name.lower().endswith(('.meta', '.rawv','.rawa', '.txt'))):
              self.num_unexp_file += 1
              self.unexp_file += (name + ' , ' )
         if(self.num_unexp_file > 0):
             self.result = False
         
         return self.result

     def serialize(self):
         super().serialize()
         self.report=self.report|{'num_unexp_file':self.num_unexp_file ,
                                   'unexp_file' : self.unexp_file }
         return self.report

class EmptyFilescheck(Check):
    def __init__(self, data , path : str) :
        super().__init__(data,path)
        
        self.code = "00103"
        self.description = " Check size of files"
        self.zero_size_file = ' '

    def run(self):
        w = walk(self.path)
        for (dirpath, dirnames, filenames) in w:
            for file in filenames: 
                file_size = os.path.getsize(dirpath+"\\"+file)
                if file_size==0:
                 self.result = False
                 self.zero_size_file += (file + ' , ')
        return self.result
    
    def serialize(self):
         super().serialize()
         self.report=self.report|{'zero_size_file':self.zero_size_file }
         return self.report

# Files checking
class RawSizeCheck(Check):
    def __init__(self, data: dict , path : str):
        super().__init__(data,path)
        self.meta_data = data['meta']
        self.txt_data = data['txt']
        self.rawv_data = data["rawv"]
        self.rawa_data = data["rawa"]

        self.code = "00201"
        self.description = " Check size of raw files"
        self.raw_file_detail = {}
        

    
    def run(self):
         frames_byte = [sublist[1] for sublist in self.txt_data]
         exp_size = (np.sum(frames_byte)) / 1024
         w = walk(self.path)
         for (dirpath, dirnames, filenames) in w:
            for file in filenames: 
                if file.lower().endswith(('.rawv','.rawa')):
                    found_size = (os.path.getsize(dirpath+"\\"+file) / 1024 )
                    if not(exp_size==found_size):
                        self.result = False
                    self.raw_file_detail= { file : { 'name' : file , 'exp_size (KB)' : int(exp_size) , 'found_size (KB)' : int(found_size)}}

         return self.result
    
    def serialize(self):
         super().serialize()
         self.report=self.report|{'raw_file_detail':self.raw_file_detail }
         return self.report
    
# Checking the number of frames is correct or not:

class NumberOfFramesCheck(Check):
        def __init__(self, data: dict , path : str):
            super().__init__(data,path)
            self.meta_data = data['meta']
            self.txt_data = data['txt']
            self.rawv_data = data["rawv"]
            
            self.code = "00301"
            self.description = " Checking the number of frames captured by the sensor"
            self.exp_frm_num = None
            self.recorded_frame_num = None
            self.frame_lost_num = None

        def run(self) -> bool:
            self.exp_frm_num=(int(self.meta_data['duration'][:2])*int(self.meta_data['framerate']))
            self.recorded_frame_num=(np.shape(self.txt_data))[0]
            self.frame_lost_num  = self.exp_frm_num - self.recorded_frame_num
            if (self.frame_lost_num ) :
                self.result = False
            
            return self.result
        
        def serialize( self ):
         super().serialize()
         self.report = self.report | {'exp_frm_num':self.exp_frm_num , 'recorded_frame_num':self.recorded_frame_num , 'frame_lost_num ':self.frame_lost_num    }
         return self.report
        
        
       
class VRecordDurationCheck(Check):
        def __init__(self, data: dict , path : str):
            super().__init__(data,path)
            self.meta_data = data['meta']
            self.txt_data = data['txt']
            self.raw_data = data["rawv"]
            self.code = "00302"
            self.description = " Checking the duration of the Video file captured by the sensor"
            self.exp_rec_duration = None
            self.act_rec_duration = None
            self.recorded_frame_num = None
            

        def run(self) -> bool:
            one_frm_duration=(1/int(self.meta_data['framerate']))*1000   # Calculating the frame duration in ms.
            self.recorded_frame_num = (np.shape(self.txt_data))[0]

            self.exp_rec_duration = (int(self.meta_data['duration'][:2]))*1000
            self.act_rec_duration = self.txt_data[self.recorded_frame_num-1][0] - self.txt_data[0][0] 

            if abs(self.exp_rec_duration - self.act_rec_duration) > one_frm_duration :
                self.result = False
            
            return self.result
        
        def serialize( self ):
         super().serialize()
         self.report = self.report | {'exp_rec_duration (ms)':self.exp_rec_duration , 'act_rec_duration (ms)':self.act_rec_duration }

         return self.report
            

class AbnormalFrameDurationCheck(Check):
     def __init__(self, data: dict , path : str):
            super().__init__(data,path)
            self.meta_data = data['meta']
            self.txt_data = data['txt']
            self.raw_data = data["rawv"]
            self.code = "00303"
            self.description = " Checking the duration of each frame and comparing it with the normal frame duration "
            self.average_frm_duration = None
            self.trsh_diff_durtion = None   #Threshold for the difference between the duration of each frame with the average duration
            self.trsh_abn_frm_durtion = 10   #Threshold for the number of abnormal frames duration           
            self.num_abn_frm_drt = 0
            self.abn_frms_drt = []

     def run(self) -> bool:
            # Calculating the number of frames that recorded by sensors
            recorded_frame_num = (np.shape(self.txt_data))[0]
            # calculating each timestamps (or each frame duration):
            timestamps=[]
            abn_frms_drt = []
            for x in range(0 ,recorded_frame_num-1):
             timestamps.append( self.txt_data[x+1][0] - self.txt_data[x][0] )

            # Searching for abnormal frame duration:
            self.average_frm_duration = sum(timestamps) / len(timestamps)

            # Defining a Treshhold for frame duration:
            self.trsh_diff_durtion = ( self.average_frm_duration / 2 )

            for frm_drt in timestamps:
             if abs ( frm_drt - self.average_frm_duration ) > self.trsh_diff_durtion :
              self.num_abn_frm_drt += 1 
              self.abn_frms_drt.append( frm_drt )

            if ( self.num_abn_frm_drt > self.trsh_abn_frm_durtion ) :
                self.result = False
                
            return self.result
        
     def serialize( self ):
         super().serialize()
         self.report = self.report | {'average_frm_duration (ms)':int(self.average_frm_duration) ,'num_abn_frm_drt':self.num_abn_frm_drt }

         return self.report


# Checking for growing monotonically
class GrowingMonotonicallyCheck(Check):
        def __init__(self, data: dict , path : str):
            super().__init__(data,path)
            self.meta_data = data['meta']
            self.txt_data = data['txt']
            self.raw_data = data["rawv"]
            self.code = "00304"
            self.description = " Checking that the duration of each frame is not monotonically"
            self.exp_rec_duration = None
            self.act_rec_duration = None
            self.recorded_frame_num = None
            

        def run(self) -> bool:
            # Calculating the number of frames that recorded by sensors
            recorded_frame_num = (np.shape(self.txt_data))[0]
            # calculating each timestamps (or each frame duration):
            timestamps=[]

            for x in range(0 ,recorded_frame_num-1):
             timestamps.append( self.txt_data[x+1][0] - self.txt_data[x][0] )
            
            is_monotonic = all(timestamps[i] <= timestamps[i+1] for i in range(len(timestamps) - 1))
            if is_monotonic:
                self.result = False
            
            return self.result
        
        def serialize( self ):
         super().serialize()

         return self.report


# Spesefic Class for Audio_kinect sensor
class ARecordDurationCheck(Check):
        def __init__(self, data: dict , path : str):
            super().__init__(data,path)
            self.meta_data = data['meta']
            self.txt_data = data['txt']
            self.rawa_data = data["rawa"]
            self.code = "00302"
            self.description = " Checking the duration of the Audio file captured by the sensor"
            self.exp_rec_duration = None
            self.act_rec_duration = None
            self.recorded_samples_num = None
            self.one_smpl_duration = None
            self.Diff_Between_duration = None

        def run(self) -> bool:
            self.one_smpl_duration=(1/int(self.meta_data['rate']))*1000   # Calculating the frame duration in ms.
            self.recorded_samples_num = (np.shape(self.txt_data))[0]

            self.exp_rec_duration = (int(self.meta_data['duration'][:2]))*1000
            self.act_rec_duration = self.txt_data[self.recorded_samples_num-1][0] - self.txt_data[0][0] 

            self.Diff_Between_duration = abs(self.exp_rec_duration - self.act_rec_duration)
            if  self.Diff_Between_duration > self.one_smpl_duration :
                self.result = False
            
            return self.result
        
        def serialize( self ):
         super().serialize()
         self.report = self.report | {'exp_rec_duration (ms)': int(self.exp_rec_duration) , 'act_rec_duration (ms)': int( self.act_rec_duration ) ,'Diff_Between_duration (ms)' : self.Diff_Between_duration, 'one_smpl_duration (ms)' : (self.one_smpl_duration)}

         return self.report

# The Main Class of checking for Calling our Ckeckers
class Checker():
    def __init__(self):
        self.data = {}
        self.report={}
        self.path = ''
        self.Failed_checks = ''

    def run(self,path:str ):
        result = True
        self.path = path

        #path_check
        abn_fld_path = AbnormalFolderInRootCheck(self.data , self.path)
        if abn_fld_path.run() == False:
            result = False
            self.Failed_checks += ' , AbnormalFolderInRootCheck'

        self.report['Root_Checking']={'AbnormalFolderInRootCheck' : abn_fld_path.serialize() }

        emp_file_path = EmptyFileInRootCheck(self.data , self.path)
        if emp_file_path.run() == False:
            result = False
            self.Failed_checks += ' , EmptyFileInRootCheck'

        self.report['Root_Checking']['EmptyFileInRootCheck'] = emp_file_path.serialize() 

        # Sensors Checking
        self.report['Sensors_checking'] = {"platfrom": "nvi","parent_folder": self.path}
        
        for name in os.listdir(self.path):
            
            # Video sensors Checker
            if (name == 'color.kinect' or name == 'depth.kinect' or name == 'ir.kinect' or name.lower() ==('depth.flexx2') or name.lower() ==('ir.flexx2') or name.lower() ==('thermal.lepton')):
                self.report['Sensors_checking'][name] = {'Folder_Checking' : {}}
                self.report['Sensors_checking'][name]['File_Checking'] = {}

                data_manager = DataManager((self.path+'\\'+name))
                if (data_manager.read() == True) :
                    self.data = data_manager.get_data()
                    # check for folder contents
                    nf_check = NumberOfFilesCheck(self.data , self.path+'\\'+name)

                    if nf_check.run() == False:
                        result = False
                        self.Failed_checks += (name+' : NumberOfFilesCheck ,')

                    self.report['Sensors_checking'][name]['Folder_Checking'] = {'NumberOfFilesCheck' : nf_check.serialize() }

                    tf_check = UnexpectedFileCheck(self.data , self.path+'\\'+name)
                    if tf_check.run() == False:
                        result = False
                        self.Failed_checks += ' , UnexpectedFileCheck'

                    self.report['Sensors_checking'][name]['Folder_Checking']['UnexpectedFileCheck'] = tf_check.serialize() 

                    
                    ef_check= EmptyFilescheck(self.data , self.path+'\\'+name)
                    if ef_check.run() == False:
                        result = False
                        self.Failed_checks += ' , EmptyFilescheck'

                    self.report['Sensors_checking'][name]['Folder_Checking']['EmptyFilescheck'] = ef_check.serialize() 

                    # Level 2 : File Checking:
                    for file_name in self.data :
                        RawSize_check = RawSizeCheck(self.data[file_name] , self.path+'\\'+name)
                        if RawSize_check.run() == False:
                         result = False
                         self.Failed_checks += ' , RawSizeCheck'

                        self.report['Sensors_checking'][name]['File_Checking'][file_name] = {'RawSizeCheck' : RawSize_check.serialize()} 

                        nframe_check = NumberOfFramesCheck(self.data[file_name] , self.path+'\\'+name)
                        if nframe_check.run() == False:
                            result = False
                            self.Failed_checks += ('File_Path:'+ name +'\\'+ file_name +' FCheck:  NumberOfFramesCheck ,')

                        self.report['Sensors_checking'][name]['File_Checking'][file_name]['NumberOfFramesCheck'] = nframe_check.serialize()


                        rec_drt_check = VRecordDurationCheck(self.data[file_name] , self.path+'\\'+name)
                        if rec_drt_check.run() == False:
                            result = False
                            self.Failed_checks += ' , VRecordDurationCheck'

                        self.report['Sensors_checking'][name]['File_Checking'][file_name]['VRecordDurationCheck'] = rec_drt_check.serialize()

                        
                        abn_frm_drt_check = AbnormalFrameDurationCheck(self.data[file_name] , self.path+'\\'+name)
                        if abn_frm_drt_check.run() == False:
                            result = False
                            self.Failed_checks += ' , AbnormalFrameDurationCheck'

                        self.report['Sensors_checking'][name]['File_Checking'][file_name]['AbnormalFrameDurationCheck'] = abn_frm_drt_check.serialize()

                        
                        growmono_check = GrowingMonotonicallyCheck(self.data[file_name] , self.path+'\\'+name)
                        if growmono_check.run() == False:
                            result = False
                            self.Failed_checks += ' , GrowingMonotonicallyCheck'

                        self.report['Sensors_checking'][name]['File_Checking'][file_name]['GrowingMonotonicallyCheck'] = growmono_check.serialize()

            '''elif (name =='audio.kinect' or name == ('audio.i2smems') ) :
                
                self.report['Sensors_checking'][name] = {'Folder_Checking' : {}}
                self.report['Sensors_checking'][name]['File_Checking'] = {}
                # Audio sensors Checker
                data_manager = DataManager((self.path+'\\'+name))
                if (data_manager.read() == True) :
                    self.data = data_manager.get_data()
                    # check for folder contents
                    nf_check = NumberOfFilesCheck(self.data , self.path+'\\'+name)

                    if nf_check.run() == False:
                        result = False
                        self.Failed_checks += ' , NumberOfFilesCheck'

                    self.report['Sensors_checking'][name]['Folder_Checking'] = {'NumberOfFilesCheck' : nf_check.serialize() }

                    tf_check = UnexpectedFileCheck(self.data , self.path+'\\'+name)
                    if tf_check.run() == False:
                        result = False
                        self.Failed_checks += ' , UnexpectedFileCheck'

                    self.report['Sensors_checking'][name]['Folder_Checking']['UnexpectedFileCheck'] = tf_check.serialize() 

                    
                    siz_check= EmptyFilescheck(self.data , self.path+'\\'+name)
                    if siz_check.run() == False:
                        result = False
                        self.Failed_checks += (name + ' : EmptyFilescheck,')

                    self.report['Sensors_checking'][name]['Folder_Checking']['EmptyFilescheck'] = siz_check.serialize() 

                    # Level 2 : File Checking:
                    for file_name in self.data :
                        RawSize_check = RawSizeCheck(self.data[file_name] , self.path+'\\'+name)
                        if RawSize_check.run() == False:
                         result = False
                         self.Failed_checks += (name + file_name +' : RawSizeCheck')

                        self.report['Sensors_checking'][name]['File_Checking'][file_name] = {'RawSizeCheck' : RawSize_check.serialize()} 

                        ''''''nframe_check = NumberOfFramesCheck(self.data[file_name] , self.path+'\\'+name)
                        if nframe_check.run() == False:
                            result = Fals
                        self.report[name]['File_Checking'][file_name]['NumberOfFramesCheck'] = nframe_check.serialize()''''''


                        rec_drt_check = ARecordDurationCheck(self.data[file_name] , self.path+'\\'+name)
                        if rec_drt_check.run() == False:
                            result = False
                            self.Failed_checks += ('File_Path:' + name +'\\'+ file_name +' FCheck: ARecordDurationCheck ,')

                        self.report['Sensors_checking'][name]['File_Checking'][file_name]['ARecordDurationCheck'] = rec_drt_check.serialize()'''

                        
        
        #check_report_struct.append(cnf_check.serialize())
        return result, self.report , self.Failed_checks
        

# The Class for preparing the Report and Export it in Json Format        
class ReportGen():
    def __init__(self, json_path: str , check_report_struct: dict , ret: bool ,check_path ,failed_check ):
        self.json_path = json_path
        self.check_path =  check_path
        self.check_report = check_report_struct
        self.final_report = {}
        self.time = Time_generator()
        self.overall_data = {}
        self.result = ret
        self.failed_check = failed_check

    def run(self):
        self.report_detail_generate()
        self.final_report["Report Details"] = self.overall_data
        self.final_report["Failed checks"] = self.failed_check
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