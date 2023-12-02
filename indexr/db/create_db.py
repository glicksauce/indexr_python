import coloredlogs
import logging
import psycopg2

from .create_table_queries import create_table_queries

# load_creds_to_environ()
coloredlogs.install()
logging.basicConfig(level="DEBUG")


def create_db(cur, conn):
    # Preparing query to create a database
    sql = """CREATE DATABASE indexr"""

    # Creating a database
    cur.execute(sql)
    print("Database created successfully........")


def create_tables(cur, conn):
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()
    logging.info("tables created successfully")


def main():
    # establishing the connection
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="password",
        host="127.0.0.1",
        port="5432",
    )
    conn.autocommit = True

    # Creating a cursor object using the cursor() method
    cur = conn.cursor()

    try:
        create_db(cur, conn)
        conn.close()
    except Exception as e:
        logging.error(f"Error creating database or retrieving associated connection and cursor: {e}")

    try:
        # connect to newly created db
        conn = psycopg2.connect(
            dbname="indexr",
            user="postgres",
            password="password",
            host="127.0.0.1",
            port="5432",
        )
        cur = conn.cursor()

        create_tables(cur, conn)
    except Exception as e:
        logging.error(f"Error creating tables: {e}")

    # Closing the connection
    conn.close()


if __name__ == '__main__':
    main()
