

try:
    import argparse
    import inspector2
except ImportError as error:
    exit(error)
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--folder_path', type=str, required=True, help='input folder ', default='')
    parser.add_argument('-e','--enable_report', type=bool, required=False, help='enable report generation', default=False)

    parser.add_argument('-j','--json_path', type=str, required=False, help='path for json file', default=0)
    parser.add_argument('-l','--light', type=bool, required=False, help='enable light mode', default=False)

    parser.add_argument('-x','--excel_path', type=str, required=True, help='input folder ', default='')

    args = parser.parse_args()
    folder_path = args.folder_path
    enable_report = args.enable_report
    json_path = args.json_path
    Light_mode = args.light
    excel_path = args.excel_path

    # do something with input_folder, output_file and sensor_id
    inspector = inspector2.Inspector_call(root_path = folder_path, enable_report = enable_report , json_path = json_path, Light_mode = Light_mode ,excel_path = excel_path )

    inspector.run()

if __name__ == "__main__":
    main()