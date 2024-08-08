import os
import argparse
from PageLoader.page_loader import download, make_dir_with_files


def page_loader_in_line():
    parser = argparse.ArgumentParser(
        description="""
            Uploads the html code from the specified web page
            to the specified directory
            """)
    parser.add_argument("--output", type=str, dest="output",
                        help='The path to the directory where the html code is saved',
                        default=os.getcwd())
    parser.add_argument("url", type=str,
                        help="The URL of the site where the html code is downloaded from")
    args = parser.parse_args()
    path_file = download(url=args.url, path_to_file=args.output)
    make_dir_with_files(url=args.url, path_to_dir=args.output)
    print(path_file)
