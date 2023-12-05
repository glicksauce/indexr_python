# mymodule.py
import logging
import os
import coloredlogs
import sys

from indexr.db.create_db import create_db_and_tables as create_db
from utils import load_creds_to_environ

# Add the parent directory of mypackage to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import subpackage.submodule

coloredlogs.install()
logging.basicConfig(level="DEBUG")


def main():
    load_creds_to_environ()
    create_db()
    input()


if __name__ == '__main__':
    main()

# to run package:
# python -m indexr.main