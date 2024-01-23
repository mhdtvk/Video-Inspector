
"""!
@file
@brief Checker for troubleshooting issues within recorded files.

This module performs various troubleshooting steps on files, returning results. 
It includes classes representing different review stages, forming a tree structure 
from the root directory to individual files. All check steps inherit from a parent class, 'Check.' 
The main class, 'Checker,' manages sensors and calls these check classes. 
Utility functions are defined to assist package operations.

@package check_levels
@author Mahdi
"""

## @defgroup Check_Levels check_levels.py
#@{

try:
    from typing import Any
    import numpy as np
    import os
    import json
    import re
    from overall_report_generator import *

except ImportError as e:
    print(f"Error: {e}")
    exit(1)


def get_folder_and_file_sizes(root_folder: str) -> dict:
    """!
    @brief Retrieve sizes of folders and files in the specified root folder.

    @param root_folder: Path to the root folder.
    @return folder_sizes: Dictionary with folder/file names as keys and their sizes as values.
    """

    folder_or_files_sizes = {}
    for item in os.listdir(root_folder):
        item_path = os.path.join(root_folder, item)
        if os.path.isdir(item_path):                # Checking if our item is directory or not
            folder_or_files_sizes[item] = sum(os.path.getsize(os.path.join(item_path, f)) for f in os.listdir(item_path))
        else:                                       # It means our item is a file
            folder_or_files_sizes[item] = os.path.getsize(item_path)
    return folder_or_files_sizes


class SetConfigurationSetting:
    """!
    @brief Import the 'configure_settings.json' file containing settings for use in our Checkers.

    This class reads the 'configure_settings.json' file and stores the data as a dictionary in JSON style.
    The data includes, for example, the threshold for each level of check.
    """

    def __init__(self) -> None:
        
        #Class constructor. Initializes the configuration data.
        
        self.read_config_data()
        self.config_data = {}

    def read_config_data(self) :
        #Read data from the 'configure_settings.json' file.
           
        with open(os.path.join(os.path.dirname(__file__), 'configure_settings.json'), 'r') as json_file:
         self.config_data = json.load(json_file)

    def set_threshold(self,checker_name:str) -> int :
        
        # Return the threshold for a given checker name.
        # param checker_name: The name of the checker for which the threshold is requested.
        # return: The threshold value.
        
        return self.config_data['threshold'][checker_name]    

# Import configuration file
set_config = SetConfigurationSetting()
set_config.read_config_data()   

class DataManager:
    """!
    @brief Class for importing data from a specified path.

    This class provides functionality to read data from various file types
    and populate DataManager attributes. It also includes a method to prepare
    data for saving.

    @note Ensure that the necessary files (meta, txt, rawa, rawv) are present
          with corresponding basenames in the specified path.
    """

    def __init__(self, path: str = "mypath"):
        
        # Initialize DataManager with a specified path and empty attributes.#
        #param path: Path to the data directory.
        
        self.path = path
        self.time = ''
        self.data = {}
        self.check_result = True

    def read(self) -> bool:
        #""!
        #brief Read data from various file types and populate DataManager attributes.

        #return: True if data reading is successful, False otherwise.
        #""
        data_managing_is_successful = True

        if not self._prepare_data_for_saving():
            data_managing_is_successful = False       

        if not self._read_raw_data():
            data_managing_is_successful = False

        if not self._read_txt_data():
            data_managing_is_successful = False

        if not self._read_metadata():
            data_managing_is_successful = False

        return data_managing_is_successful

    def _prepare_data_for_saving(self) -> bool :
        #""!
        #brief Prepare data for saving by identifying valid sets of files.#
        #return: True if valid data sets are identified, False otherwise.
        #""

        recorded_files = os.listdir(self.path)
        recorded_basename = {os.path.splitext(file)[0] for file in recorded_files}

        for basename in recorded_basename :
            if (f'{basename}.meta') in recorded_files and (f'{basename}.txt') in recorded_files and {(f'{basename}.rawv') in recorded_files or (f'{basename}.rawa') in recorded_files} :
                self.data[basename] = {'rawa' : [], 'rawv' : [], 'txt' : [], 'meta' : []}

        return bool(self.data)
    
    def _read_raw_data(self) -> bool:
        #""!
        #brief Read raw data files (.rawv, .rawa) and populate DataManager data attribute.

        #return: True if reading raw data is successful, False otherwise.
        #""
        ret = True
        for filename in self.data:
                data = []
                self.data[filename]['rawa'] = data
                self.data[filename]['rawv'] = data

                if self.data[filename]['rawv'] == {} and self.data[filename]['rawa'] == {}:
                    
                    ret = False
        return ret

    def _read_txt_data(self) -> bool:
        #""!
        #brief Read .txt data files and populate DataManager data attribute.

        #return: True if reading .txt data is successful, False otherwise.
        #""

        ret = True
        for filename in self.data:
            data = []
            with open(os.path.join(self.path, f'{filename}.txt'), "r") as file:
                    for line in file:
                        columns = line.strip().split(' ')
                        row = [int(col) for col in columns]
                        data.append(row)
            file.close()
            self.data[filename]['txt'] = data

        if not self.data:
            ret = False

        return ret

    def _read_metadata(self) -> bool:
        #""!
        #brief Read .meta files and populate DataManager data attribute.

        #return: True if reading .meta files is successful, False otherwise.
        #""
        ret = True
        for filename in self.data:
                data = {}
                with open(os.path.join(self.path, f'{filename}.meta'), "r") as file:
                    for line in file:
                        columns = line.strip().split(' ')
                        data[columns[0]] = columns[1]
                file.close()
                self.data[filename]['meta'] = data

        if not self.data:
            ret = False

        return ret

    def get_data(self) -> dict:
        #""
        #brief Get the DataManager data attribute.

        #return: Dictionary containing collected data.
        #""
        return self.data


class Check:
    """!
    @brief Parent class for each level of checking.

    This class serves as the parent for individual check levels. It includes
    attributes for storing information about the check, such as code, description,
    result, and a report. The class also provides a method to serialize check results
    into a report.

    @note Subclasses should override the 'run_check' method to implement specific checks.
    """

    def __init__(self, data: dict, path: str):
        #""!
        #brief Class constructor.

        #param data: Dictionary containing collected data.
        #param path: Path to the data directory.
        #""
        self.path = path
        self.code = None
        self.description = None
        self.result = True
        self.report = {}

    def serialize(self) -> dict:
        #""!
        #brief Serialize check results into a report.

        #return: Report containing check details.
        #""
        self.report = self.report | {'code': self.code, "description": self.description, "Result": self.result}
        return self.report


class AbnormalFolderInRootCheck(Check):
    """!
    @brief Class for checking abnormal folders in the root directory.

    This class is a subclass of the Check class and focuses on checking
    for abnormal folders in the root directory. It includes methods for running
    the check, serializing detailed and light check results into reports.

    @note Subclasses should override the 'run' method to implement specific checks.
    """

    def __init__(self, data: dict, path: str):
        #""!
        #brief Class constructor.

        #param data: Dictionary containing collected data.
        #param path: Path to the data directory.
        #""
        super().__init__(data, path)
        self.code = "00001"
        self.description = "Checking the Root Folder for abnormal Files or Folders"
        self.num_unexp_file = 0
        self.unexp_file = ''

    def run(self) -> bool:
        #""!
        #brief Run the check to identify unexpected files.

        #return: True if no unexpected files found, False otherwise.
        #""
        for name in os.listdir(self.path):
            if name.lower() not in ('audio.kinect', 'color.kinect', 'depth.kinect', 'ir.kinect', 'audio.i2smems', 'depth.flexx2', 'ir.flexx2', 'thermal.lepton'):
                self.num_unexp_file += 1 
                self.unexp_file += (name + ' , ')

        if self.num_unexp_file > 0:
            self.result = False
        return self.result
    
    def detailed_serialize(self) -> dict:
        #""!
        #brief Serialize detailed check results into a report.

        #return: Detailed report containing unexpected file details.
        #""
        super().serialize()
        self.report = self.report | {'num_unexp_file': self.num_unexp_file, 'unexp_file': self.unexp_file}
        return self.report
    
    def light_serialize(self) -> dict:
        #""!
        #brief Serialize light check results into a report.

        #return: Light report containing basic check details.
        #""
        super().serialize()
        return self.report


class EmptyFileInRootCheck(Check):
    """!
    @brief Class for checking empty files in the root directory.

    This class is a subclass of the Check class and focuses on checking
    for empty files in the root directory. It includes methods for running
    the check, serializing detailed and light check results into reports.

    @note Subclasses should override the 'run' method to implement specific checks.
    """

    def __init__(self, data: dict, path: str):
        #""!
        #brief Class constructor.

        #param data: Dictionary containing collected data.
        #param path: Path to the data directory.
        #""
        super().__init__(data, path)
        self.code = "00002"
        self.description = "Checking the Root Folder for abnormal Folder Size"
        self.zero_size_folder = ''

    def run(self) -> bool:
        #""!
        #brief Run the check to identify folders with zero size.

        #return: True if no zero-size folders found, False otherwise.
        #""
        sizes = get_folder_and_file_sizes(self.path)
        for name in sizes:
            if sizes[name] == 0:
                self.result = False
                self.zero_size_folder += (name + ' , ')
        return self.result
    
    def detailed_serialize(self) -> dict:
        #""!
        #brief Serialize detailed check results into a report.

        #return: Detailed report containing folders with zero size.
        #""
        super().serialize()
        self.report = self.report | {'zero_size_folder': self.zero_size_folder}
        return self.report

    def light_serialize(self) -> dict:
        #""!
        #brief Serialize light check results into a report.

        #return: Light report containing basic check details.
        #""
        super().serialize()
        return self.report




class NumberOfFilesCheck(Check):
    """!
    @brief Class for checking the number of files.

    This class is a subclass of the Check class and focuses on checking
    the number of expected files against the actual number of files
    present in the specified path. It includes methods for running
    the check, serializing detailed and light check results into reports.

    @note Subclasses should override the 'run' method to implement specific checks.
    """

    def __init__(self, data: dict, path: str):
        #""!
        #brief Class constructor.

        #param data: Dictionary containing collected data.
        #param path: Path to the data directory.
        #""
        super().__init__(data, path)
        self.meta_data = data['00000000']['meta']
        self.code = "00101"
        self.description = "Check number of files"
        self.num_found_file = 0
        self.num_exp_file = 0
        self.num_raw_exp_files = 0
        self.num_raw_found_files = 0
        self.num_meta_exp_files = 0
        self.num_meta_found_files = 0
        self.num_txt_exp_files = 0
        self.num_txt_found_files = 0

    def run(self) -> bool:
        #""!
        #brief Run the number of files check.

        #return: True if the number of files check is successful, False otherwise.
        #""
        self.num_file_found = len(os.listdir(self.path))

        pattern = re.compile(r'file:\s+\d+/(\d+)')
        txt_meta_data = "\n".join(f"{key}: {value}" for key, value in self.meta_data.items())
        
        match = pattern.search(txt_meta_data)
        
        if match:
            # Extract the value before the slash from the match
            file_value = int(match.group(1))

        self.num_exp_file = 3 * file_value

        if self.num_file_found != self.num_exp_file:
            self.result = False

        self.num_raw_exp_files = file_value
        for name in os.listdir(self.path):
            if name.lower().endswith(('.rawv', '.rawa')):
                self.num_raw_found_files += 1

        if not (self.num_raw_exp_files == self.num_raw_found_files):
            self.result = False

        self.num_meta_exp_files = file_value
        for name in os.listdir(self.path):
            if name.lower().endswith('.meta'):
                self.num_meta_found_files += 1

        if self.num_meta_exp_files != self.num_meta_found_files:
            self.result = False

        self.num_txt_exp_files = file_value
        for name in os.listdir(self.path):
            if name.lower().endswith('.txt'):
                self.num_txt_found_files += 1

        if self.num_txt_exp_files != self.num_txt_found_files:
            self.result = False

        return self.result

    def detailed_serialize(self) -> dict:
        #""!
        #brief Serialize detailed check results into a report.

        #return: Detailed report containing information about expected
        #        and found files.
        #""
        super().serialize()
        self.report = self.report | {
            "num_exp_file": self.num_exp_file,
            "num_file_found": self.num_file_found,
            "num_raw_exp_files": self.num_raw_exp_files,
            "num_raw_found_files": self.num_raw_found_files,
            "num_meta_exp_files": self.num_meta_exp_files,
            "num_meta_found_files": self.num_meta_found_files,
            "num_txt_exp_files": self.num_txt_exp_files,
            "num_txt_found_files": self.num_txt_found_files
        }
        return self.report

    def light_serialize(self) -> dict:
        #""!
        #brief Serialize light check results into a report.

        #return: Light report containing basic check details.
        #""
        super().serialize()
        return self.report

     

class UnexpectedFileCheck(Check):
    """!
    @brief Class for checking unexpected file types.

    This class is a subclass of the Check class and focuses on checking
    the types of files in the specified path. It includes methods for running
    the check, serializing detailed and light check results into reports.

    @note Subclasses should override the 'run' method to implement specific checks.
    """

    def __init__(self, data, path: str):
    
        super().__init__(data, path)
        self.code = "00102"
        self.description = "Check type of files"
        self.num_unexp_file = 0
        self.unexp_file = ''

    def run(self) -> bool:
        
        for name in os.listdir(self.path):
            if not (name.lower().endswith(('.meta', '.rawv', '.rawa', '.txt'))):
                self.num_unexp_file += 1
                self.unexp_file += (name + ' , ')
        if self.num_unexp_file > 0:
            self.result = False
        
        return self.result

    def detailed_serialize(self) -> dict:
        
        super().serialize()
        self.report = self.report |  {
            'num_unexp_file': self.num_unexp_file,
            'unexp_file': self.unexp_file
        }
        return self.report
     
    def light_serialize(self) -> dict:
        
        super().serialize()
        return self.report



class EmptyFilesCheck(Check):
    """!
    @brief Class for checking empty files.

    This class is a subclass of the Check class and focuses on checking
    the size of files in the specified path. It includes methods for running
    the check, serializing detailed and light check results into reports.

    @note Subclasses should override the 'run' method to implement specific checks.
    """

    def __init__(self, data, path: str):
        
        super().__init__(data, path)
        self.code = "00103"
        self.description = "Check size of files"
        self.zero_size_file = ' '

    def run(self) -> bool:
         
        w = os.walk(self.path)
        for (dirpath, dirnames, filenames) in w:
            for file in filenames:
                file_size = os.path.getsize(dirpath + "/" + file)
                if file_size == 0:
                    self.result = False
                    self.zero_size_file += (file + ' , ')
        return self.result
    
    def detailed_serialize(self) -> dict:
         
        super().serialize()
        self.report = self.report | {
            'zero_size_file': self.zero_size_file
        }
        return self.report
    
    def light_serialize(self) -> dict:
         
        super().serialize()
        return self.report


class IrDepthFrameNumberConsistencyCheck(Check):
    """!
    @brief Class for checking consistency between IR and depth sensors Frame Numbers.

    This class checks if IR and depth sensors (e.g., ir.sensorX and depth.sensorX) have the same number of frames.
    """

    def __init__(self, data: dict, file_name, path: str, second_sensor_path):
         
        super().__init__(data, path)
        self.code = "00011"
        self.description = "Checking to verify if ir.sensorX and depth.sensorX have the same number of frames"
        self.file_name = file_name  # 00000, 00001, ...

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

        self.difference_threshold = set_config.set_threshold("IrDepthFrameNumberConsistencyCheck")  # %
        self.difference = None  # the

    def run(self) -> bool:
         
        second_sensor_data_manager = DataManager(self.second_sensor_path)
        if second_sensor_data_manager.read():
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

        self.difference = (abs(1 - (self.first_sensor_recorded_frame_num / self.second_sensor_recorded_frame_num)) * 100)

        if self.difference_threshold < self.difference:
            self.result = False

        return self.result

    def detailed_serialize(self) -> dict:
         
        super().serialize()
        self.report = self.report | {
            'first_sensor_name': self.first_sensor_name,
            'second_sensor_name': self.second_sensor_name,
            'first_sensor_recorded_frame_num': self.first_sensor_recorded_frame_num,
            'second_sensor_recorded_frame_num': self.second_sensor_recorded_frame_num,
            'Difference_threshold %': self.difference_threshold,
            'Difference %': self.difference
        }
        return self.report

    def light_serialize(self) -> dict:
         
        super().serialize()
        return self.report

    

class IrDepthTimestampsConsistencyCheck(Check):
    """!
    @brief Class for checking consistency between IR and depth sensors Timestamps.

    This class checks if IR and depth sensors (e.g., ir.sensorX and depth.sensorX) have the same timestamps.
    """

    def __init__(self, data: dict, file_name, path: str, second_sensor_path):
         
        super().__init__(data, path)
        self.code = "00012"
        self.description = "Checking to verify if ir.sensorX and depth.sensorX have the same timestamps. "
        self.file_name = file_name  # 00000, 00001, ...

        self.first_sensor_data = data
        self.second_sensor_data = None

        self.first_sensor_path = path
        self.second_sensor_path = second_sensor_path

        self.first_sensor_name = os.path.basename(path)
        self.second_sensor_name = os.path.basename(second_sensor_path)

        self.unmatched_timestamps_number = None

        self.matching_percentage_threshold = set_config.set_threshold("IrDepthTimestampsConsistencyCheck")  # %
        self.matching_percentage = None  # the

        self.first_sensor_txt_data = data[self.file_name]['txt']
        self.second_sensor_txt_data = None

    def run(self) -> bool:
         
        second_sensor_data_manager = DataManager(self.second_sensor_path)
        if second_sensor_data_manager.read():
            self.second_sensor_data = second_sensor_data_manager.get_data()

        self.second_sensor_txt_data = self.second_sensor_data[self.file_name]['txt']

        timestamps_first_sensor = set([sub_array[0] for sub_array in self.first_sensor_txt_data])
        timestamps_second_sensor = set([sub_array[0] for sub_array in self.second_sensor_txt_data])

        intersection = timestamps_first_sensor.intersection(timestamps_second_sensor)
        self.matching_percentage = (len(intersection) / len(timestamps_first_sensor)) * 100
        self.unmatched_timestamps_number = len(timestamps_first_sensor) - len(intersection)

        if self.matching_percentage < self.matching_percentage_threshold:
            self.result = False

        return self.result

    def detailed_serialize(self) -> dict:
         
        super().serialize()
        self.report = self.report | {
            'first_sensor_name': self.first_sensor_name,
            'second_sensor_name': self.second_sensor_name,
            'matching_percentage (%)': self.matching_percentage,
            'unmatched_timestamps_number': self.unmatched_timestamps_number,
            'matching_percentage_threshold (%)': self.matching_percentage_threshold
        }
        return self.report

    def light_serialize(self) -> dict:
         
        super().serialize()
        return self.report



        
class RawSizeCheck(Check):
    """!
    @brief Class to check the size of raw files.

    This class checks the size of raw files and compares it with the expected size based on metadata.
    """

    def __init__(self, data: dict, path: str):
         
        super().__init__(data, path)
        self.meta_data = data['meta']
        self.txt_data = data['txt']
        self.rawv_data = data["rawv"]
        self.rawa_data = data["rawa"]
        self.difference_trsh = set_config.set_threshold("RawSizeCheck")
        self.code = "00201"
        self.description = "Check size of raw files"
        self.raw_file_detail = {}

    def run(self) -> bool:
         
        frames_byte = [sublist[1] for sublist in self.txt_data]
        exp_size = (np.sum(frames_byte)) / 1024
        w = os.walk(self.path)
        for (dirpath, dirnames, filenames) in w:
            for file in filenames:
                if file.lower().endswith(('.rawv', '.rawa')):
                    found_size = (os.path.getsize(dirpath+"/"+file) / 1024)
                    if self.difference_trsh < (abs(1 - int(found_size)/int(exp_size))*100):
                        self.result = False
                    self.raw_file_detail = {file: {'name': file, 'exp_size (KB)': int(exp_size),
                                                   'found_size (KB)': int(found_size),
                                                   'Difference_trsh %': self.difference_trsh,
                                                   'Difference %': "{:.2f}".format(((1 - int(found_size) / int(exp_size)) * 100))}}

        return self.result

    def detailed_serialize(self) -> dict:
         
        super().serialize()
        self.report = self.report | {'raw_file_detail': self.raw_file_detail}
        return self.report

    def light_serialize(self) -> dict:
         
        super().serialize()
        return self.report



class NumberOfFramesCheck(Check):
    """
    @brief Class to check the number of frames captured by the sensor.

    This class checks the number of frames captured by the sensor and compares it with the expected number based on metadata.
    """

    def __init__(self, data: dict, path: str):
         
        super().__init__(data, path)
        self.meta_data = data['meta']
        self.txt_data = data['txt']
        self.rawv_data = data["rawv"]
        self.difference_trsh = set_config.set_threshold("NumberOfFramesCheck")  # %
        self.code = "00301"
        self.description = "Checking the number of frames captured by the sensor"
        self.exp_frm_num = None
        self.recorded_frame_num = None
        self.difference_num_frame = None
        self.difference = None

    def run(self) -> bool:
         
        index_s = self.meta_data['duration'].find('s')
        self.exp_frm_num = (int(self.meta_data['duration'][:index_s]) * int(self.meta_data['framerate']))
        self.recorded_frame_num = (np.shape(self.txt_data))[0]
        self.difference_num_frame = abs(self.exp_frm_num - self.recorded_frame_num)
        self.difference = (abs(1 - self.recorded_frame_num / self.exp_frm_num) * 100)
        if self.difference_trsh < self.difference:
            self.result = False

        return self.result

    def detailed_serialize(self) -> dict:
         
        super().serialize()
        self.report = self.report | {'exp_frm_num': self.exp_frm_num,
                                     'recorded_frame_num': self.recorded_frame_num,
                                     'difference_num_frame': self.difference_num_frame,
                                     'Difference_threshold %': self.difference_trsh,
                                     'Difference %': self.difference}
        return self.report

    def light_serialize(self) -> dict:
         
        super().serialize()
        return self.report

       
        
       
class VRecordDurationCheck(Check):
    """!
    @brief Class to check the duration of the Video file captured by the sensor.

    This class checks the duration of the video file captured by the sensor and compares it with the expected duration based on metadata.
    """

    def __init__(self, data: dict, path: str):
         
        super().__init__(data, path)
        self.meta_data = data['meta']
        self.txt_data = data['txt']
        self.raw_data = data["rawv"]
        self.code = "00302"
        self.description = "Checking the duration of the Video file captured by the sensor"
        self.exp_rec_duration = None
        self.act_rec_duration = None
        self.recorded_frame_num = None
        self.difference_trsh = set_config.set_threshold("VRecordDurationCheck")
        self.difference = None  # %

    def run(self) -> bool:
         
        index_s = self.meta_data['duration'].find('s')
        self.recorded_frame_num = (np.shape(self.txt_data))[0]

        self.exp_rec_duration = (int(self.meta_data['duration'][:index_s])) * 1000
        self.act_rec_duration = self.txt_data[self.recorded_frame_num - 1][0] - self.txt_data[0][0]
        self.difference = (abs(1 - self.act_rec_duration / self.exp_rec_duration) * 100)

        if self.difference_trsh < self.difference:
            self.result = False

        return self.result

    def detailed_serialize(self) -> dict:
         
        super().serialize()
        self.report = self.report | {'exp_rec_duration (ms)': self.exp_rec_duration,
                                     'act_rec_duration (ms)': self.act_rec_duration,
                                     'Difference_threshold %': self.difference_trsh,
                                     'Difference %': self.difference}
        return self.report

    def light_serialize(self) -> dict:
         
        super().serialize()
        return self.report



class AbnormalFrameDurationCheck(Check):
    """!
    @brief Class to check the duration of each frame and compare it with the normal frame duration.

    This class checks the duration of each frame in the sensor data and compares it with the expected frame duration.
    """

    def __init__(self, data: dict, path: str):
         
        super().__init__(data, path)
        self.meta_data = data['meta']
        self.txt_data = data['txt']
        self.raw_data = data["rawv"]
        self.code = "00303"
        self.description = "Checking the duration of each frame and comparing it with the normal frame duration"
        self.configured_frm_duration = None
        self.duration_difference_threshold = None
        self.ratio_trsh = set_config.set_threshold("AbnormalFrameDurationCheck")  # Threshold for the number of abnormal frames duration in %
        self.num_abn_frm_drt = 0
        self.abn_frms_drt = []
        self.recorded_frame_num = 0
        self.ratio = 0

    def run(self) -> bool:
         
        self.recorded_frame_num = (np.shape(self.txt_data))[0]
        timestamps = []
        abn_frms_drt = []
        for x in range(0, self.recorded_frame_num - 1):
            timestamps.append(self.txt_data[x + 1][0] - self.txt_data[x][0])

        self.configured_frm_duration = (1 / int(self.meta_data['framerate'])) * 1000
        self.duration_difference_threshold = (self.configured_frm_duration / 2)

        for frm_drt in timestamps:
            if abs(frm_drt - self.configured_frm_duration) > self.duration_difference_threshold:
                self.num_abn_frm_drt += 1
                self.abn_frms_drt.append(frm_drt)

        self.ratio = ((self.num_abn_frm_drt / self.recorded_frame_num) * 100)
        if self.ratio_trsh < self.ratio:
            self.result = False

        return self.result

    def detailed_serialize(self) -> dict:
         
        super().serialize()
        self.report = self.report | {'configured_fram_duration (ms)': int(self.configured_frm_duration),
                                     'duration_difference_threshold': self.duration_difference_threshold,
                                     'recorded_frame_num': self.recorded_frame_num,
                                     'num_abn_frm_drt': self.num_abn_frm_drt,
                                     'Ratio_threshold (abnormal / normal)%': self.ratio_trsh,
                                     'Ratio (abnormal / normal)%': self.ratio}
        return self.report

    def light_serialize(self) -> dict:
         
        super().serialize()
        return self.report



class GrowingMonotonicallyCheck(Check):
    """!
    @brief Class to check that the duration of each frame is not monotonically.

    This class checks whether the duration of each frame is monotonically increasing or not.
    """

    def __init__(self, data: dict, path: str):
         
        super().__init__(data, path)
        self.meta_data = data['meta']
        self.txt_data = data['txt']
        self.raw_data = data["rawv"]
        self.code = "00304"
        self.description = "Checking that the duration of each frame is not monotonically"
        self.exp_rec_duration = None
        self.act_rec_duration = None
        self.recorded_frame_num = None

    def run(self) -> bool:
         
        # Calculating the number of frames recorded by sensors
        recorded_frame_num = (np.shape(self.txt_data))[0]
        # Calculating each timestamps (or each frame duration):
        timestamps = [self.txt_data[x + 1][0] - self.txt_data[x][0] for x in range(0, recorded_frame_num - 1)]

        is_monotonic = all(timestamps[i] <= timestamps[i + 1] for i in range(len(timestamps) - 1))
        if is_monotonic:
            self.result = False

        return self.result

    def detailed_serialize(self) -> dict:
         
        super().serialize()

        return self.report

    def light_serialize(self) -> dict:
         
        super().serialize()
        return self.report



class ARecordDurationCheck(Check):
    """!
    @brief Class to check the duration of the Audio file captured by the sensor.

    This class checks whether the duration of the audio file matches the expected duration based on metadata.
    """

    def __init__(self, data: dict, path: str):
        
        super().__init__(data, path)
        self.meta_data = data['meta']
        self.txt_data = data['txt']
        self.rawa_data = data["rawa"]
        self.code = "00302"
        self.description = "Checking the duration of the Audio file captured by the sensor"
        self.exp_rec_duration = None
        self.act_rec_duration = None
        self.recorded_samples_num = None
        self.one_smpl_duration = None
        self.Diff_Between_duration = None

    def run(self) -> bool:
         
        self.one_smpl_duration = (1 / int(self.meta_data['rate'])) * 1000  # Calculating the frame duration in ms.
        self.recorded_samples_num = (np.shape(self.txt_data))[0]

        self.exp_rec_duration = (int(self.meta_data['duration'][:2])) * 1000
        self.act_rec_duration = self.txt_data[self.recorded_samples_num - 1][0] - self.txt_data[0][0]

        self.Diff_Between_duration = abs(self.exp_rec_duration - self.act_rec_duration)
        if self.Diff_Between_duration > self.one_smpl_duration:
            self.result = False

        return self.result

    def detailed_serialize(self) -> dict:
         
        super().serialize()
        self.report = self.report | {'exp_rec_duration (ms)': int(self.exp_rec_duration),
                                     'act_rec_duration (ms)': int(self.act_rec_duration),
                                     'Diff_Between_duration (ms)': self.Diff_Between_duration,
                                     'one_smpl_duration (ms)': self.one_smpl_duration}

        return self.report

    def light_serialize(self) -> dict:
         
        super().serialize()
        return self.report


class Checker:
    """!
    @brief Main class of the package to manage all the level of checkers.

    This class is the main part of this package. It checks the names of the sensors
    and calls the appropriate checkers and processes the result to build a report.
    """

    def __init__(self, path="mypath", light_mode=True):
         
        self.data = {}
        self.report = {}
        self.excel_report = {}
        self.path = path
        self.light_mode = light_mode
        self.result = True
        self.setting_data = None
        self.overall_reprot = OverallReprot()

    def run(self):
        
        """!
        @brief Run the checker for all the Sensor files.

        
        This method traverses through the directory structure starting from the root where the recorded files are stored. It systematically examines the information within each file recorded by the sensor, ensuring comprehensive troubleshooting.

        The method is organized into three main parts:

        1. **Root Review:**
        At the root level, the method checks for specific conditions or abnormalities related to the overall structure of the recorded files. The results of these checks are saved in the appropriate format for processing, either as a lightweight JSON report or a detailed one, along with Excel reports.

        2. **Folder Review:**
        For each sensor type, such as 'depth.kinect', 'ir.kinect', 'depth.flexx2', 'ir.flexx2', and 'thermal.lepton', the method performs checks at the folder level. It examines the contents of each folder to identify any unexpected files, empty files, or any other conditions that may require attention. The results are saved in JSON and Excel reports.

        3. **File Review:**
        At the file level, the method conducts various checks for each recorded file. These checks include ensuring the correct number of frames, verifying file sizes, validating frame durations, and examining other specific characteristics. The results of these checks are again saved in the appropriate JSON and Excel reports.

        This systematic approach allows for a thorough troubleshooting process, providing detailed insights into any issues or inconsistencies present in the recorded files. The reports generated serve as valuable documentation for further analysis and corrective actions.



        @return: Tuple containing the result, detailed report, and Excel report.
        """
        # Loading overall report for adding new data:
        self.overall_reprot.load_state()
        # Root checking
        self.excel_report['Root_Checking'] = {}
        root_report = {}
        root_result = True

        # AbnormalFolderInRootCheck
        abn_fld_path = AbnormalFolderInRootCheck(self.data, self.path)
        abn_fld_path_result = abn_fld_path.run()
        self.excel_report['Root_Checking']['AbnormalFolderInRootCheck'] = abn_fld_path_result

        if not abn_fld_path_result:
            root_result = False
            self.overall_reprot.add_new_error('AbnormalFolderInRootCheck')
        root_report['AbnormalFolderInRootCheck'] = abn_fld_path.light_serialize() if self.light_mode else abn_fld_path.detailed_serialize()

        # EmptyFileInRootCheck
        emp_file_path = EmptyFileInRootCheck(self.data, self.path)
        emp_file_path_result = emp_file_path.run()
        self.excel_report['Root_Checking']['EmptyFileInRootCheck'] = emp_file_path_result

        if not emp_file_path_result:
            root_result = False
            self.overall_reprot.add_new_error('EmptyFileInRootCheck')
        root_report['EmptyFileInRootCheck'] = emp_file_path.light_serialize() if self.light_mode else emp_file_path.detailed_serialize()

        self.report['Root_Checking'] = {'Status': root_result}
        self.report['Root_Checking']['Checkers'] = root_report

        self.result = root_result

        # Sensors Checking
        self.report['Sensors_checking'] = {}
        sensor_check_result = True


        for name in os.listdir(self.path):
            if name in ['depth.kinect', 'ir.kinect', 'depth.flexx2', 'ir.flexx2', 'thermal.lepton']:
                sensor_report = {'Folder_Checking': {}, 'File_Checking': {}}
                sensor_data_manager = DataManager(os.path.join(self.path, name))
                if sensor_data_manager.read():
                    self.data = sensor_data_manager.get_data()

                    # NumberOfFilesCheck
                    num_files_check = NumberOfFilesCheck(self.data, os.path.join(self.path, name))
                    nf_check_result = num_files_check.run()
                    if not nf_check_result:
                        sensor_check_result = False
                        self.overall_reprot.add_new_error('NumberOfFilesCheck', name)

                    sensor_report['Folder_Checking']['NumberOfFilesCheck'] = (num_files_check.light_serialize() if self.light_mode else num_files_check.detailed_serialize())
                    self.excel_report[name] = {'NumberOfFilesCheck': bool(nf_check_result)}

                    # UnexpectedFileCheck
                    tf_check = UnexpectedFileCheck(self.data, os.path.join(self.path, name))
                    tf_check_res = tf_check.run()
                    if not tf_check_res:
                        sensor_check_result = False
                        self.overall_reprot.add_new_error('UnexpectedFileCheck', name)

                    sensor_report['Folder_Checking']['UnexpectedFileCheck'] = (tf_check.light_serialize() if self.light_mode else tf_check.detailed_serialize())
                    self.excel_report[name]['UnexpectedFileCheck'] = tf_check_res

                    # EmptyFilescheck
                    ef_check = EmptyFilesCheck(self.data, os.path.join(self.path, name))
                    ef_check_res = ef_check.run()
                    if not ef_check_res:
                        sensor_check_result = False
                        self.overall_reprot.add_new_error('EmptyFilesCheck', name)


                    sensor_report['Folder_Checking']['EmptyFilesCheck'] = (ef_check.light_serialize() if self.light_mode else ef_check.detailed_serialize())
                    self.excel_report[name]['EmptyFilesCheck'] = ef_check_res
                    
                    # Level 2: File Checking
                    for file_name in self.data:
                        sensor_report['File_Checking'][file_name] = {}
                        
                        # ir_depth_frame_number_consistency_check for: Kinect Sensor
                        if name == 'depth.kinect':
                            frm_num_consis_check = IrDepthFrameNumberConsistencyCheck(self.data, file_name, os.path.join(self.path, name), os.path.join(self.path, 'ir.kinect'))
                            frm_num_consis_check_result = frm_num_consis_check.run()
                            if not frm_num_consis_check_result:
                                sensor_check_result = False
                                self.overall_reprot.add_new_error('kinect_ir_depth_frame_number_consistency_check', name)
                    
                            sensor_report['File_Checking'][file_name]['kinect_ir_depth_frame_number_consistency_check'] = (frm_num_consis_check.light_serialize() if self.light_mode else frm_num_consis_check.detailed_serialize())
                            self.excel_report[name]['kinect_ir_depth_frame_number_consistency_check'] = frm_num_consis_check_result
                    
                        # ir_depth_frame_number_consistency_check for: Flexx2 Sensor
                        if name == 'depth.flexx2':
                            frm_num_consis_check = IrDepthFrameNumberConsistencyCheck(self.data, file_name, os.path.join(self.path, name), os.path.join(self.path, 'ir.flexx2'))
                            frm_num_consis_check_result = frm_num_consis_check.run()
                            if not frm_num_consis_check_result:
                                sensor_check_result = False
                                self.overall_reprot.add_new_error('flexx2_ir_depth_frame_number_consistency_check', name)
                    
                            sensor_report['File_Checking'][file_name]['flexx2_ir_depth_frame_number_consistency_check'] = (frm_num_consis_check.light_serialize() if self.light_mode else frm_num_consis_check.detailed_serialize())
                            self.excel_report[name]['flexx2_ir_depth_frame_number_consistency_check'] = frm_num_consis_check_result

                        
                        # ir_depth_timestamp_consistency_check for: Flexx2 Sensor
                        if name == 'depth.flexx2':
                            timstmp_consis_check = IrDepthTimestampsConsistencyCheck(self.data, file_name, os.path.join(self.path, name), os.path.join(self.path, 'ir.flexx2'))
                            timstmp_consis_check_result = timstmp_consis_check.run()
                            if not timstmp_consis_check_result:
                                sensor_check_result = False
                                self.overall_reprot.add_new_error('flexx2_ir_depth_timestamps_consistency_check', name)
                    
                            sensor_report['File_Checking'][file_name]['flexx2_ir_depth_timestamps_consistency_check'] = (timstmp_consis_check.light_serialize() if self.light_mode else timstmp_consis_check.detailed_serialize())
                            self.excel_report[name]['flexx2_ir_depth_timestamps_consistency_check'] = timstmp_consis_check_result

                        # ir_depth_timestamp_consistency_check for: Kinect Sensor
                        if name == 'depth.kinect':
                            timstmp_consis_check = IrDepthTimestampsConsistencyCheck(self.data, file_name, os.path.join(self.path, name), os.path.join(self.path, 'ir.kinect'))
                            timstmp_consis_check_result = timstmp_consis_check.run()
                            if not timstmp_consis_check_result:
                                sensor_check_result = False
                                self.overall_reprot.add_new_error('kinect_ir_depth_timestamps_consistency_check', name)
                    
                            sensor_report['File_Checking'][file_name]['kinect_ir_depth_timestamps_consistency_check'] = (timstmp_consis_check.light_serialize() if self.light_mode else timstmp_consis_check.detailed_serialize())
                            self.excel_report[name]['kinect_ir_depth_timestamps_consistency_check'] = timstmp_consis_check_result

                        # RawSizeCheck
                        RawSize_check = RawSizeCheck(self.data[file_name], os.path.join(self.path, name))
                        RawSize_check_res = RawSize_check.run()
                        if not RawSize_check_res:
                            sensor_check_result = False
                            self.overall_reprot.add_new_error('RawSizeCheck', name)

                        sensor_report['File_Checking'][file_name]['RawSizeCheck'] = RawSize_check.light_serialize() if self.light_mode else RawSize_check.detailed_serialize()
                        self.excel_report[name]['RawSizeCheck'] = RawSize_check_res
                    
                        # NumberOfFramesCheck
                        if name != "thermal.lepton":
                            nframe_check = NumberOfFramesCheck(self.data[file_name], os.path.join(self.path, name))
                            nframe_check_res = nframe_check.run()
                            if not nframe_check_res:
                                sensor_check_result = False
                                self.overall_reprot.add_new_error('NumberOfFramesCheck', name)
                    
                            sensor_report['File_Checking'][file_name]['NumberOfFramesCheck'] = (nframe_check.light_serialize() if self.light_mode else nframe_check.detailed_serialize())
                            self.excel_report[name]['NumberOfFramesCheck'] = bool(nframe_check_res)

                        # VRecordDurationCheck
                        rec_drt_check = VRecordDurationCheck(self.data[file_name], os.path.join(self.path, name))
                        rec_drt_check_res = rec_drt_check.run()
                        if not rec_drt_check_res:
                            sensor_check_result = False
                            self.overall_reprot.add_new_error('VRecordDurationCheck', name)

                        sensor_report['File_Checking'][file_name]['VRecordDurationCheck'] = (rec_drt_check.light_serialize() if self.light_mode else rec_drt_check.detailed_serialize())
                        self.excel_report[name]['VRecordDurationCheck'] = rec_drt_check_res

                        # AbnormalFrameDurationCheck
                        abn_frm_drt_check = AbnormalFrameDurationCheck(self.data[file_name], os.path.join(self.path, name))
                        abn_frm_drt_check_res = abn_frm_drt_check.run()
                        if not abn_frm_drt_check_res:
                            sensor_check_result = False
                            self.overall_reprot.add_new_error('AbnormalFrameDurationCheck', name)

                        sensor_report['File_Checking'][file_name]['AbnormalFrameDurationCheck'] = (abn_frm_drt_check.light_serialize() if self.light_mode else abn_frm_drt_check.detailed_serialize())
                        self.excel_report[name]['AbnormalFrameDurationCheck'] = abn_frm_drt_check_res

                        # GrowingMonotonicallyCheck
                        growmono_check = GrowingMonotonicallyCheck(self.data[file_name], os.path.join(self.path, name))
                        growmono_check_res = growmono_check.run()
                        if not growmono_check_res:
                            sensor_check_result = False
                            self.overall_reprot.add_new_error('GrowingMonotonicallyCheck', name)

                        sensor_report['File_Checking'][file_name]['GrowingMonotonicallyCheck'] = (growmono_check.light_serialize() if self.light_mode else growmono_check.detailed_serialize())
                        self.excel_report[name]['GrowingMonotonicallyCheck'] = growmono_check_res

                        # Reporting
                        self.report['Sensors_checking'][name] = {'Status': sensor_check_result}
                        self.report['Sensors_checking'][name]['Checkers'] = sensor_report
                        self.result = sensor_check_result


        # Saving overall report for storing new data:
        self.overall_reprot.save_state()

        return self.result ,self.report, self.excel_report
    
# @} ##