# mymodule.py
import os
import sys
# Add the parent directory of mypackage to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import subpackage.submodule

from indexr.db.create_db import main as create_db
from .utils import load_creds_to_environ


def main():
    load_creds_to_environ()
    create_db()
    input()

if __name__ == '__main__':
    main()

# to run package:
# python -m indexr.main