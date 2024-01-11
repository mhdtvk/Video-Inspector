
try:
    from inspector import *
    import argparse
except ImportError as e:
    print(f"Error: {e}")
    exit(1)


def main():
    """
    Parses command-line arguments to run the Inspector.
    """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--folder_path', type=str, required=True, help='input folder ', default='')
        parser.add_argument('-e', '--enable_report', required=False, help='enable report generation', default=False)
        parser.add_argument('-j', '--json_path', type=str, required=False, help='path for json file', default=0)
        parser.add_argument('-l', '--light', required=False, help='enable light mode', default=False)
        parser.add_argument('-x', '--excel_path', type=str, required=True, help='input folder ', default='')

        args = parser.parse_args()
        folder_path = args.folder_path
        enable_report = True if args.enable_report == 'true' else False
        json_path = args.json_path
        light_mode = True if args.light == 'true' else False
        excel_path = args.excel_path

        inspector = Inspector(root_path=folder_path, enable_report=enable_report, json_path=json_path, light_mode=light_mode, excel_path=excel_path)
        inspector.run()

    except ImportError as error:
        exit(error)

if __name__ == "__main__":
    main()
