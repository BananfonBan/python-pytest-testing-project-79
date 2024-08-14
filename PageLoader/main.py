import os
import argparse
import logging
from PageLoader.page_loader import download, make_dir_with_files

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s|%(levelname)s|%(filename)s|%(funcName)s:%(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.DEBUG)


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
    parser.add_argument("--nolocal", action="store_true",
                        help="If enabled, resources from third-party domains\
                            used on this page will also be downloaded")
    args = parser.parse_args()
    only_local = False if args.nolocal else True
    path_file = download(url=args.url, path_to_file=args.output)
    make_dir_with_files(url=args.url, path_to_dir=args.output,
                        only_local_content=only_local)
    print(path_file)
