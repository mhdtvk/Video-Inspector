
![stronghold logo](https://github.com/omarzandona/record_inspector/assets/37227181/3fe37146-3d36-497d-b79d-2bf34e9bc6e8)

## Badges
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# Inspector Project

Inspector is a Python program designed to check the performance of the sensors and files recorded by audio and video sensors. It aims to find bugs, issues, or unusual events and is intended for use as part of a larger project.

## Technologies and Libraries

Inspector leverages the following libraries:
- argparse    1.1
- tqdm        4.66.1
- time
- typing
- numpy      1.26.2
- os
- json       2.0.9
- re
- openpyxl   3.1.2
- pandas     2.1.4
- pip        22.0.2

The shell script `run_inspector.sh` is used to interact with the end-user.

## Installation

To install and start using the program, follow these steps:
1. Install the required libraries.
2. Download the built-in modules.
3. Execute the Bash file named `run_inspector.sh`.

## Usage

Run the program using the provided Bash script:

```bash
./run_inspector.sh
```

The program will prompt you to enter necessary information, such as the path of recorded files and other configurable settings. After entering the values, the program will run and display a short result. Reports in Excel and JSON formats will be generated and saved at the end of the program.

## Modules

### 1. run_inspector.sh

- Shell script for invoking the Inspector module and running it in a loop.
- Interacts with the user, takes input values, and displays a summary of results.

### 2. main_inspector.py

- Uses the argparse library to manage user input data in the correct format.

### 3. inspector.py

- Connects the main parts of the program.
- Checks the file directory and sends it to the `check_levels.py` file.
- Produces reports in JSON and Excel formats.

### 4. check_levels.py

- Retrieves recorded files and saves them in a reviewable format.
- Performs all review steps on the data and returns the result.

### 5. excel_generator.py

- Saves the report file in Excel format.
- Includes design sections for readability and summary preparation.

## Configuration
Users can customize program settings by changing the configure_settings.json file, including the threshold to determine the level of unusualness recognized as an error.

## Example
For example, if the FPS (frames per second) in a recorded video is lower than the set threshold for the sensor, Inspector will report it as an error.

```python
# class NumberOfFramesCheck( ):

 difference = (abs(1 - recorded_frame_num / exp_frm_num) * 100)
        if difference_trsh < difference:
            result = False
```

## File Structure
The project files and directory are organized, and the results (Excel and JSON reports) are placed in a user-chosen path.

## Contributions
Inspector is a private project, but contributions, comments, and changes can be suggested through issues and pull requests for those with repository access.

## License
All assets and code are under the MIT License.

## Additional Resources
All rights of this project belong to [EVS Technology Company](https://www.embeddedvisionsystems.it/). For more information, visit [EVS Technology Company's website](https://www.embeddedvisionsystems.it/).



