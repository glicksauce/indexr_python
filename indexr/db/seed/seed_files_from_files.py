import os
from os import walk
import datetime
import logging
import psycopg2
import urllib.parse
import xattr

from ..schema.schema import DBName


# path to files we wish to tag
LOCAL_ROOT_INDEX = os.environ.get("local_root_index")
REMOTE_ROOT_INDEX = "https://www.dropbox.com/home"

# specific directory to filter to from LOCAL_ROOT_INDEX
SUFFIX = os.environ.get("local_root_suffix")
ROOT_INDEX_LOCATION = LOCAL_ROOT_INDEX + SUFFIX


def seed_files_from_files():
    logging.info("starting 'seed_files_from_files'")
    try:
        conn = psycopg2.connect(
            dbname=DBName.name,
            user="postgres",
            password=os.environ["root_db_pw"],
            host="localhost",
            port="5432",
        )
    except Exception:
        print("I am unable to connect to the database")

    cur = conn.cursor()

    f = []
    for (dirpath, dirnames, filenames) in walk(ROOT_INDEX_LOCATION):
        dirpath_sanitized = dirpath.replace("'", "''")
        for f in filenames:
            filetype = f.split(".")[-1].lower()
            size = os.path.getsize(f"{dirpath}/{f}")
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(f"{dirpath}/{f}"))
            created = datetime.datetime.fromtimestamp(os.path.getctime(f"{dirpath}/{f}"))
            test = xattr.xattr((f"{dirpath}/{f}")).list()
            f_sanitized = f.replace("'", "''")
            remote_url = urllib.parse.quote_plus(REMOTE_ROOT_INDEX + SUFFIX)
            logging.debug(f"{dirpath}/{f}, {filetype}, {size}, {test}, {remote_url}")
            try:
                cur.execute(
                    f"INSERT INTO files (hash, url, file, filetype)"
                    f"VALUES ('testhash', 'testurl', '{dirpath_sanitized}/{f_sanitized}', '{filetype}')"
                )
                conn.commit()
            except Exception as e:
                logging.warning(f"error inserting into files table: {e}")
                conn.rollback()

        # if "''" in dirpath:
        #     break
        # f.extend(filenames)

    conn.close()
    cur.close()
