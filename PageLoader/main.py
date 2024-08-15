import os
import argparse
import logging
import PageLoader.page_loader


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
                        help="Determines which logging level will be used.\
                        By default, INFO", default="INFO")
    args = parser.parse_args()
    log_level = getattr(logging, f"{args.loglevel.upper()}", "INFO")
    logging.basicConfig(
        format='%(asctime)s|%(levelname)s|%(filename)s|%(funcName)s:%(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=log_level)
    only_local = False if args.nonlocal_ else True
    PageLoader.page_loader.full_download(url=args.url, path=args.output,
                                         only_local_content=only_local)


page_loader_in_line()
