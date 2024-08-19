import os
import sys
import argparse
import logging
import requests
from .page_loader import make_dir_with_content, download


logger = logging.getLogger(__name__)


def main(url, path, only_local_content=True): # noqa C901
    logger.info(f"requested url:{url}")
    logger.info(f"output path: {path}")
    try:
        path_html_page = download(url=url, path_to_file=path, main_link=True)
    except requests.exceptions.HTTPError:
        logger.critical(f"HTTP Error\nurl={url}")
        sys.exit(1)
    except requests.exceptions.ReadTimeout:
        logger.critical(f"Time out\nurl={url}")
        sys.exit(0)
    except requests.exceptions.ConnectionError:
        logger.critical(f"Connection error\nurl={url}")
        sys.exit(0)
    except requests.RequestException:
        logger.critical(f"The url content could not be downloaded\nurl={url}")
        sys.exit(0)
    except PermissionError:
        logger.critical("You don't have permission to do this")
        sys.exit(1)
    except FileExistsError:
        logger.critical("Such a file already exists")
        sys.exit(1)
    except FileNotFoundError:
        logger.critical("The specified directory does not exist")
        sys.exit(1)
    logger.info(f"write html file: {path_html_page}")
    try:
        make_dir_with_content(url=url, path_to_dir=path,
                              only_local_content=only_local_content)
    except PermissionError:
        logger.critical("You do not have the appropriate rights to create directory")
        sys.exit(1)
    except FileExistsError:
        logger.critical("Such a directory already exists")
        sys.exit(1)
    except FileNotFoundError:
        sys.exit(1)
    else:
        logger.info("The download was successful")


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
    parser.add_argument("--nonlocal", action="store_true", dest="nonlocal_",
                        help="If enabled, resources from third-party domains\
                            used on this page will also be downloaded")
    parser.add_argument("--log", type=str, dest="loglevel",
                        help="Determines which logging level will be used..\
                        By default, INFO", default="INFO")
    args = parser.parse_args()
    log_level = getattr(logging, f"{args.loglevel.upper()}", "INFO")
    logging.basicConfig(
        format='[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)3d %(levelname)7s - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=log_level)
    only_local = False if args.nonlocal_ else True
    main(url=args.url, path=args.output,
         only_local_content=only_local)
