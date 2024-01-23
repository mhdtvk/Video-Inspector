##========================================================================= 
#
#@package overall_report_generator
#@author Mahdi
#@date jan-2024
#@brief 
#========================================================================= 
import pickle


class OverallReprot :
    def __init__(self) -> None:
        self.total_file_number = {}
        self.total_file_volume = {}
        self.numebr_of_errors = 0
        self.error_types = {}
        self.faulty_sensors = {}
        

    
    def add_new_error(self, error_type : str, sensor_name : str = '-'):
        
        ## Documentation for a method 
        #  
        # @brief With this method, we add the found error to the list of errors.
        # @param error_type : The name of the error found. E.g. : ( AbnormalFolderInRootCheck , ...)
        # @param sensor_name : The name of the sensor in which the error was found. If errors are found in the root files; The error name remains empty.

        # Variable:'numebr_of_errors' : The number of errors is stored in this variable
        self.numebr_of_errors += 1

        # Variable:'error_types' : Add to the number of errors found for the error type. If the error name is not already in the dictionary; we add.
        if error_type in self.error_types :
            self.error_types[error_type] += 1
        else:
            self.error_types[error_type] = 1

        # Variable:'faulty_sensors' : It is added to the number of errors found for the faulty sensor. If it is not already in the dictionary; we add
        if sensor_name in self.faulty_sensors :
            self.faulty_sensors[sensor_name] += 1

        else:
            self.faulty_sensors[sensor_name] = 1


    def add_new_file(self, file_type : str, file_volume : int):

        #### Documentation for a method 
        #  
        # @brief With this method, we count the number of checked files. We also calculate the volume of checked 'rawv' data.
        # @param file_type : Checked file type.  E.g. : ( rawv, rawa, ...)
        # @param file_volume : Checked file size.

        if file_type == 'rawv':
            if file_type in self.total_file_volume :

                self.total_file_number[file_type] += 1
                self.total_file_volume[file_type] += file_volume
            else:
                self.total_file_number[file_type] = 1
                self.total_file_volume[file_type] = file_volume

    def save_state(self, file_path: str = 'overall_report_state.pkl') -> None:
        """!
        Documentation for a method :

        @brief Save the state of the OverallReprot instance to a file using pickle.
        @param file_path (str): The path to the file where the state will be saved.
        """
        with open(file_path, 'wb') as file:
            pickle.dump(self.__dict__, file)

    def load_state(self, file_path: str = 'overall_report_state.pkl') -> None:
        """!
        Documentation for a method :

        @brief Load the state of the OverallReprot instance from a file using pickle.
        @param file_path (str): The path to the file from which the state will be loaded.
        """
        try:
            with open(file_path, 'rb') as file:
                state = pickle.load(file)
                self.__dict__.update(state)
        except (FileNotFoundError, pickle.UnpicklingError) as e:
            print(f"Error loading state from {file_path}: {e}")


    def print_final_data(self):
        """
        Documentation for the function:

        @brief Print the final data from the OverallReprot instance for the user.

        @param overall_report_instance (OverallReprot): The OverallReprot instance containing the data.
        """
        print("=== Final Report ===")

        print(f"Total Number of Files Checked: {self.total_file_number}")

        print(f"Total Volume of Checked Files:")
        for file_type, volume in self.total_file_volume.items():
            print(f"  - {file_type}: {volume} bytes")

        print(f"Number of Errors Found: {self.numebr_of_errors}")

        print("Error Types:")
        for error_type, count in self.error_types.items():
            print(f"  - {error_type}: {count} errors")

        print("Faulty Sensors:")
        for sensor_name, count in self.faulty_sensors.items():
            print(f"  - {sensor_name}: {count} errors")
    


    def main(self):

        self.load_state()
        self.print_final_data()


if __name__ == "__main__":
    overall_report = OverallReprot()
    overall_report.main()


    
