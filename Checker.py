from typing import Any
import numpy as np
import os
from os import walk




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
                with open(self.path+'/'+file_name, "r") as file:
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
                with open(self.path+'/'+file_name, "r") as file:
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
    
    def detailed_serialize(self):
         super().serialize()
         self.report=self.report|{'num_unexp_file':self.num_unexp_file ,
                                   'unexp_file' : self.unexp_file }
         return self.report
    
    def light_serialize(self):
         super().serialize()
         
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
    
    def detailed_serialize(self):
         super().serialize()
         self.report=self.report|{'zero_size_folder':self.zero_size_folder }
         return self.report

    def light_serialize(self):
         super().serialize()
         
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

    def detailed_serialize(self):
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
    
    def light_serialize(self):
         super().serialize()
         
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

     def detailed_serialize(self):
         super().serialize()
         self.report=self.report|{'num_unexp_file':self.num_unexp_file ,
                                   'unexp_file' : self.unexp_file }
         return self.report
     
     def light_serialize(self):
         super().serialize()
         
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
                file_size = os.path.getsize(dirpath+"/"+file)
                if file_size==0:
                 self.result = False
                 self.zero_size_file += (file + ' , ')
        return self.result
    
    def detailed_serialize(self):
         super().serialize()
         self.report=self.report|{'zero_size_file':self.zero_size_file }
         return self.report
    
    def light_serialize(self):
         super().serialize()
         
         return self.report

# Files checking
    
#_ir_depth_consistency_check
class ir_depth_consistency_check(Check):
    def __init__(self, data: dict , file_name ,path: str , second_sensor_path ):
        super().__init__(data, path)
        self.code = "00011"
        self.description = " Checking to verify if ir.sensorX and detph.sensorX have the same number of frame or not"
        
        self.file_name = file_name #00000,00001,...

        self.first_sensor_data = data
        self.second_sensor_data = None

        self.first_sensor_path = path
        self.second_sensor_path = second_sensor_path

        self.first_sensor_name = os.path.basename(path)
        self.second_sensor_name = os.path.basename(second_sensor_path)

        self.first_sensor_exp_frm_num = None
        self.first_sensor_recorded_frame_num = None

        self.second_sensor_exp_frm_num = None
        self.second_sensor_recorded_frame_num = None

        self.difference_trsh = 1 # %
        self.difference = None   # the 


    def run( self ) -> bool:

        second_sensor_data_manager = DataManager(self.second_sensor_path)
        if (second_sensor_data_manager.read() == True) :
            self.second_sensor_data = second_sensor_data_manager.get_data()

        
        first_sensor_frame_num = NumberOfFramesCheck(self.first_sensor_data[self.file_name], self.first_sensor_path)
        second_sensor_frame_num = NumberOfFramesCheck(self.second_sensor_data[self.file_name], self.second_sensor_path)

        first_sensor_frame_num.run()
        first_sensor_details = first_sensor_frame_num.detailed_serialize()

        second_sensor_frame_num.run()
        second_sensor_details = second_sensor_frame_num.detailed_serialize()

        
        self.first_sensor_exp_frm_num = first_sensor_details['exp_frm_num']
        self.first_sensor_recorded_frame_num = first_sensor_details['recorded_frame_num']

        self.second_sensor_exp_frm_num = second_sensor_details['exp_frm_num']
        self.second_sensor_recorded_frame_num = second_sensor_details['recorded_frame_num']

        self.difference = (abs(1-(self.first_sensor_recorded_frame_num/self.second_sensor_recorded_frame_num))* 100)
        
        if self.difference_trsh < self.difference :
                self.result = False
            
        return self.result
        
    def detailed_serialize( self ):
         super().serialize()
         self.report = self.report | {'first_sensor_name':self.first_sensor_name , 'second_sensor_name':self.second_sensor_name , 'first_sensor_recorded_frame_num ':self.first_sensor_recorded_frame_num , 'second_sensor_recorded_frame_num ':self.second_sensor_recorded_frame_num  , 'Difference_trsh %' : self.difference_trsh ,'Difference %' : self.difference }
         return self.report
    
    def light_serialize(self):
         super().serialize()
         
         return self.report
        
class RawSizeCheck(Check):
    def __init__(self, data: dict , path : str):
        super().__init__(data,path)
        self.meta_data = data['meta']
        self.txt_data = data['txt']
        self.rawv_data = data["rawv"]
        self.rawa_data = data["rawa"]
        self.difference_trsh = 15
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
                    found_size = (os.path.getsize(dirpath+"/"+file) / 1024 )
                    if self.difference_trsh < (abs(1 - int(found_size)/int(exp_size))*100):
                        self.result = False
                    self.raw_file_detail= { file : { 'name' : file , 'exp_size (KB)' : int(exp_size) , 'found_size (KB)' : int(found_size) ,'Difference_trsh %' : self.difference_trsh, 'Difference %' : "{:.2f}".format(((1 - int(found_size)/int(exp_size))*100)) }}

         return self.result
    
    def detailed_serialize(self):
         super().serialize()
         self.report=self.report|{'raw_file_detail':self.raw_file_detail }
         return self.report
    
    def light_serialize(self):
         super().serialize()
         
         return self.report
    
# Checking the number of frames is correct or not:

class NumberOfFramesCheck(Check):
        def __init__(self, data: dict , path : str):
            super().__init__(data,path)
            self.meta_data = data['meta']
            self.txt_data = data['txt']
            self.rawv_data = data["rawv"]
            self.difference_trsh = 1 # %
            self.code = "00301"
            self.description = " Checking the number of frames captured by the sensor"
            self.exp_frm_num = None
            self.recorded_frame_num = None
            self.frame_lost_num = None
            self.difference = None 

        def run(self) -> bool:
            index_s = self.meta_data['duration'].find('s')
            self.exp_frm_num=(int(self.meta_data['duration'][:index_s])*int(self.meta_data['framerate']))
            self.recorded_frame_num=(np.shape(self.txt_data))[0]
            self.frame_lost_num  = abs(self.exp_frm_num - self.recorded_frame_num)
            self.difference = (abs(1 - self.recorded_frame_num/self.exp_frm_num)* 100)
            if self.difference_trsh < self.difference :
                self.result = False
            
            return self.result
        
        def detailed_serialize( self ):
         super().serialize()
         self.report = self.report | {'exp_frm_num':self.exp_frm_num , 'recorded_frame_num':self.recorded_frame_num , 'frame_lost_num ':self.frame_lost_num  , 'Difference_trsh %' : self.difference_trsh ,'Difference %' : self.difference }
         return self.report
        
        def light_serialize(self):
         super().serialize()
         
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
            self.difference_trsh = 15

            

        def run(self) -> bool:
            index_s = self.meta_data['duration'].find('s')
            self.recorded_frame_num = (np.shape(self.txt_data))[0]

            self.exp_rec_duration = (int(self.meta_data['duration'][:index_s]))*1000
            self.act_rec_duration = self.txt_data[self.recorded_frame_num-1][0] - self.txt_data[0][0] 

            if self.difference_trsh < (abs(1 - self.act_rec_duration/self.exp_rec_duration) *100)  :
                self.result = False
            
            return self.result
        
        def detailed_serialize( self ):
         super().serialize()
         self.report = self.report | {'exp_rec_duration (ms)':self.exp_rec_duration , 'act_rec_duration (ms)':self.act_rec_duration , 'Difference_trsh %' : self.difference_trsh ,'Difference %' : 1 - self.act_rec_duration/self.exp_rec_duration }

         return self.report
        
        def light_serialize(self):
         super().serialize()
         
         return self.report
            

class AbnormalFrameDurationCheck(Check):
     def __init__(self, data: dict , path : str):
            super().__init__(data,path)
            self.meta_data = data['meta']
            self.txt_data = data['txt']
            self.raw_data = data["rawv"]
            self.code = "00303"
            self.description = " Checking the duration of each frame and comparing it with the normal frame duration "
            self.configured_frm_duration = None
            self.durationـdifferenceـthreshold = None   #Threshold for the difference between the duration of each frame with the average duration
            self.ratio_trsh = 15   #Threshold for the number of abnormal frames duration in %           
            self.num_abn_frm_drt = 0
            self.abn_frms_drt = []
            self.recorded_frame_num = 0
            self.ratio = 0

     def run(self) -> bool:
            # Calculating the number of frames that recorded by sensors
            self.recorded_frame_num = (np.shape(self.txt_data))[0]
            # calculating each timestamps (or each frame duration):
            timestamps=[]
            abn_frms_drt = []
            for x in range(0 ,self.recorded_frame_num-1):
             timestamps.append( self.txt_data[x+1][0] - self.txt_data[x][0] )

            # Searching for abnormal frame duration:
            self.configured_frm_duration = (1 / int(self.meta_data['framerate']))*1000

            # Defining a Treshhold for frame duration:
            self.durationـdifferenceـthreshold = ( self.configured_frm_duration / 2 )

            for frm_drt in timestamps:
             if abs ( frm_drt - self.configured_frm_duration ) > self.durationـdifferenceـthreshold :
              self.num_abn_frm_drt += 1 
              self.abn_frms_drt.append( frm_drt )

            self.ratio  = ((self.num_abn_frm_drt/self.recorded_frame_num)*100)
            if  self.ratio_trsh < self.ratio :
                self.result = False
                
            return self.result
        
     def detailed_serialize( self ):
         super().serialize()
         self.report = self.report | {'configured_fram_duration (ms)':int(self.configured_frm_duration) ,'duration_difference_threshold':self.durationـdifferenceـthreshold,'recorded_frame_num' : self.recorded_frame_num,'num_abn_frm_drt':self.num_abn_frm_drt ,'Ratio_threshold (abnormal / normal)%' :self.ratio_trsh, 'Ratio (abnormal / normal)%' : self.ratio }

         return self.report
     
     def light_serialize(self):
         super().serialize()
         
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
        
        def detailed_serialize( self ):
         super().serialize()

         return self.report
        
        def light_serialize(self):
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
        
        def detailed_serialize( self ):
         super().serialize()
         self.report = self.report | {'exp_rec_duration (ms)': int(self.exp_rec_duration) , 'act_rec_duration (ms)': int( self.act_rec_duration ) ,'Diff_Between_duration (ms)' : self.Diff_Between_duration, 'one_smpl_duration (ms)' : (self.one_smpl_duration)}

         return self.report
        
        def light_serialize(self):
         super().serialize()
         
         return self.report

# The Main Class of checking for Calling our Ckeckers
class Checker():
    def __init__(self, path: str = "mypath", Light_mode = True):
        self.data = {}
        self.report={}
        self.excel_report = {}
        self.path = path
        self.Light_mode = Light_mode

    def run(self):


        # Root_checking
        self.excel_report['Root_Checking'] = {}
        root_report = {}
        root_result = True

        #AbnormalFolderInRootCheck
        abn_fld_path = AbnormalFolderInRootCheck(self.data , self.path)
        abn_fld_path_result = abn_fld_path.run()

        self.excel_report['Root_Checking']['AbnormalFolderInRootCheck'] = abn_fld_path_result


        if abn_fld_path_result == False:
            root_result = False

        root_report['AbnormalFolderInRootCheck'] = (abn_fld_path.light_serialize() if self.Light_mode else abn_fld_path.detailed_serialize() )


        #EmptyFileInRootCheck
        emp_file_path = EmptyFileInRootCheck(self.data , self.path)
        emp_file_path_result = emp_file_path.run()
        self.excel_report['Root_Checking']['EmptyFileInRootCheck'] = emp_file_path_result

        if emp_file_path_result == False:
            root_result = False

        root_report['EmptyFileInRootCheck'] = (emp_file_path.light_serialize() if self.Light_mode else emp_file_path.detailed_serialize() ) 


        #Appending Root Report and Result:
        self.report['Root_Checking'] = {'Status': root_result}
        self.report['Root_Checking']['Checkers'] = root_report
        
        result = root_result
        #

        # Sensors Checking
        self.report['Sensors_checking'] = {}
        sensor_check_result = True

        for name in os.listdir(self.path):
            
            # Video sensors Checker
            if (name == 'depth.kinect' or name == 'ir.kinect' or name.lower() ==('depth.flexx2') or name.lower() ==('ir.flexx2') or name.lower() ==('thermal.lepton')):
                sensor_report  = {'Folder_Checking' : {}}
                sensor_report['File_Checking'] = {}

                data_manager = DataManager((self.path+'/'+name))
                if (data_manager.read() == True) :

                    self.data = data_manager.get_data()

                    # NumberOfFilesCheck
                    nf_check = NumberOfFilesCheck(self.data , self.path+'/'+name)
                    nf_check_result = nf_check.run()
                    if nf_check_result == False:
                        sensor_check_result = False

                    sensor_report['Folder_Checking']['NumberOfFilesCheck'] = (nf_check.light_serialize() if self.Light_mode else nf_check.detailed_serialize() )
                    self.excel_report[name] = {'NumberOfFilesCheck' : bool(nf_check_result)}

                    #UnexpectedFileCheck
                    tf_check = UnexpectedFileCheck(self.data , self.path+'/'+name)
                    tf_check_res = tf_check.run()
                    if tf_check_res == False:
                        sensor_check_result = False

                    sensor_report['Folder_Checking']['UnexpectedFileCheck'] = (tf_check.light_serialize() if self.Light_mode else tf_check.detailed_serialize() ) 
                    self.excel_report[name]['UnexpectedFileCheck'] = tf_check_res

                    #EmptyFilescheck
                    ef_check= EmptyFilescheck(self.data , self.path+'/'+name)
                    ef_check_res = ef_check.run()
                    if ef_check_res  == False:
                        sensor_check_result = False

                    sensor_report['Folder_Checking']['EmptyFilescheck'] = (ef_check.light_serialize() if self.Light_mode else ef_check.detailed_serialize() )  
                    self.excel_report[name]['EmptyFilescheck'] = ef_check_res

                    # Level 2 : File Checking:
                    for file_name in self.data :
                        sensor_report['File_Checking'][file_name] = {}
                        # ir_depth_consistency_check for: Kinect Sensor
                        if name == 'depth.kinect':
                            consis_check = ir_depth_consistency_check(self.data ,file_name, self.path+'/'+name , self.path+'/'+ 'ir.kinect' )
                            consis_check_result = consis_check.run()
                            if consis_check_result == False:
                                sensor_check_result = False

                            sensor_report['File_Checking'][file_name]['kinect_ir_depth_consistency_check'] = (consis_check.light_serialize() if self.Light_mode else consis_check.detailed_serialize() )  
                            self.excel_report[name]['kinect_ir_depth_consistency_check'] = consis_check_result

                        # ir_depth_consistency_check for: Flexx2 Sensor
                        if name == 'depth.flexx2' :
                            consis_check = ir_depth_consistency_check(self.data ,file_name, self.path+'/'+name , self.path+'/'+ 'ir.flexx2')
                            consis_check_result = consis_check.run()
                            if consis_check_result == False:
                                sensor_check_result = False

                            sensor_report['File_Checking'][file_name]['flexx2_ir_depth_consistency_check'] = (consis_check.light_serialize() if self.Light_mode else consis_check.detailed_serialize() )  
                            self.excel_report[name]['flexx2_ir_depth_consistency_check'] = consis_check_result

                        #RawSizeCheck
                        RawSize_check = RawSizeCheck(self.data[file_name] , self.path+'/'+name)
                        RawSize_check_res = RawSize_check.run()
                        if RawSize_check_res == False:
                         sensor_check_result = False

                        sensor_report['File_Checking'][file_name]['RawSizeCheck'] = (RawSize_check.light_serialize() if self.Light_mode else RawSize_check.detailed_serialize() )
                        self.excel_report[name]['RawSizeCheck'] = RawSize_check_res

                        #NumberOfFramesCheck
                        if name != "thermal.lepton" :
                            nframe_check = NumberOfFramesCheck(self.data[file_name] , self.path+'/'+name)
                            nframe_check_res = nframe_check.run()
                            if nframe_check_res == False:
                                sensor_check_result = False

                            sensor_report['File_Checking'][file_name]['NumberOfFramesCheck'] = (nframe_check.light_serialize() if self.Light_mode else nframe_check.detailed_serialize() )
                            self.excel_report[name]['NumberOfFramesCheck'] = bool(nframe_check_res)

                        #VRecordDurationCheck
                        rec_drt_check = VRecordDurationCheck(self.data[file_name] , self.path+'/'+name)
                        rec_drt_check_res = rec_drt_check.run()
                        if rec_drt_check_res == False:
                            sensor_check_result = False

                        sensor_report['File_Checking'][file_name]['VRecordDurationCheck'] = (rec_drt_check.light_serialize() if self.Light_mode else rec_drt_check.detailed_serialize() )
                        self.excel_report[name]['VRecordDurationCheck'] = rec_drt_check_res

                        #AbnormalFrameDurationCheck
                        abn_frm_drt_check = AbnormalFrameDurationCheck(self.data[file_name] , self.path+'/'+name)
                        abn_frm_drt_check_res = abn_frm_drt_check.run()
                        if abn_frm_drt_check_res == False:
                            sensor_check_result = False

                        sensor_report['File_Checking'][file_name]['AbnormalFrameDurationCheck'] = (abn_frm_drt_check.light_serialize() if self.Light_mode else abn_frm_drt_check.detailed_serialize() )
                        self.excel_report[name]['AbnormalFrameDurationCheck'] = abn_frm_drt_check_res

                        #GrowingMonotonicallyCheck
                        growmono_check = GrowingMonotonicallyCheck(self.data[file_name] , self.path+'/'+name)
                        growmono_check_res = growmono_check.run()
                        if  growmono_check_res == False:
                            sensor_check_result = False

                        sensor_report['File_Checking'][file_name]['GrowingMonotonicallyCheck'] = (growmono_check.light_serialize() if self.Light_mode else growmono_check.detailed_serialize() )
                        self.excel_report[name]['GrowingMonotonicallyCheck'] = growmono_check_res
       
                #
                self.report['Sensors_checking'][name] = {'Status': sensor_check_result}
                self.report['Sensors_checking'][name]['Checkers'] = sensor_report
                result = sensor_check_result
                        
        


        #check_report_struct.append(cnf_check.serialize())
        return result ,self.report, self.excel_report
        