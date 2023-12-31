# mymodule.py
import logging
import os
import coloredlogs
import sys

from indexr.utils import load_creds_to_environ


# Add the parent directory of mypackage to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import subpackage.submodule

coloredlogs.install()
logging.basicConfig(level="DEBUG")


def main():
    load_creds_to_environ()

    # input()
    # seed tables
    from indexr.db.seed import seed_tags, seed_files_from_files, seed_tags_files
    seed_files_from_files()
    seed_tags_files()
    seed_tags()


main()

# to run package:
# python -m indexr.main
