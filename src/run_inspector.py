# inputs:
#  - path to the directory containing the files to be inspected
#  - optionally config file path
# outputs:
#  - console output

import argparse
from pathlib import Path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python application to inspect the sanity of video/audio raw records')
    parser.add_argument('path', type=str, help='path to the directory containing the files to be inspected')
    parser.add_argument('-c', '--config', type=str, default="", help='path to the config file')
    args = parser.parse_args()


    # check if path exists
    path = Path(args.path)
    if not path.exists() or not path.is_dir():
        exit("Directory does not exist: {}".format(args.path))


    # check if config file exists if specified
    if args.config != "":
        config_path = Path(args.config)
        if not config_path.exists() or not config_path.is_file():
            exit("Config file does not exist: {}".format(args.config))

   # Invoke the inspector
   raw_rec_insp = Inspector(path, args.config_path)
   raw_rec_insp.run()
