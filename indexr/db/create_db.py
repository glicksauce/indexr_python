import psycopg2
import psycopg2.extras
import logging
import os

from schema.create_table_queries import create_table_queries
from schema.schema import DBName

class DatabaseManipulation:
    def __init__(self):
        self.new_conn()

    def __del__(self):
        logging.debug("closing db connection")
        self.conn.close()

    def new_conn(self):
        try:
            conn = psycopg2.connect(
                user="postgres",
                password=os.environ["root_db_pw"],
                host="localhost",
                port="5432",
            )
            conn.autocommit = True
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            self.conn = conn
            self.cur = cur
        except Exception:
            print("I am unable to connect to the database")
            raise

    def new_db_conn(self):
        # close existing connection if any
        try:
            self.conn.close()
        except Exception as e:
            logging.debug("unable to close existing connection", e)

        try:
            conn = psycopg2.connect(
                database=DBName.name,
                user="postgres",
                password=os.environ["root_db_pw"],
                host="localhost",
                port="5432",
            )
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            self.conn = conn
            self.cur = cur
        except Exception:
            print("I am unable to connect to the database")
            raise

    def create_db(self):
        try:
            # Preparing query to create a database
            sql = """CREATE DATABASE indexr"""

            # Creating a database
            self.cur.execute(sql)
            self.conn.commit()
            logging.info("Indexr Database created successfully........")
            return True
        except Exception as e:
            logging.warning(f"unable to create indexr db: {e}")
            return False

    def drop_db(self):
        # Preparing query to create a database
        sql = """DROP DATABASE indexr with (force)"""

        # Creating a database
        self.cur.execute(sql)
        self.conn.commit()

    def create_tables(self):
        print('start create tables')
        for query in create_table_queries:
            self.cur.execute(query)
            self.conn.commit()
        verify_tables_query = "SELECT count(*) FROM files"
        self.cur.execute(verify_tables_query)
        print("verify table creation", self.cur.fetchall())
        logging.info("tables created successfully")


if __name__ == '__main__':
    import coloredlogs
    coloredlogs.install()
    logging.basicConfig(level="DEBUG")
    from indexr.utils import load_creds_to_environ
    load_creds_to_environ()

    # create DB and tables
    db_mainipulation_class = DatabaseManipulation()
    db_mainipulation_class.drop_db()
    db_mainipulation_class.create_db()
    db_mainipulation_class.new_db_conn()
    db_mainipulation_class.create_tables()

    # # seed tables
    # from indexr.db.seed import seed_files_from_files
    # import seed.seed_tags_files
    # import seed.seed_tags_table
    # seed_files_from_files()
    # seed.seed_tags_files()
    # seed.seed_tags_table()
