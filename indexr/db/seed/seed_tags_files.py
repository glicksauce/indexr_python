#!/usr/bin/python
import os
import logging
import psycopg2

SEED_SQL = [
    """
    INSERT INTO tags_files (files_id, tags_id)
    VALUES (3, 1)
    """,
    """
    INSERT INTO tags_files (files_id, tags_id)
    VALUES (1, 2)
    """
]


def seed_tags_files():
    logging.info("starting 'seed_tags_files'")
    try:
        conn = psycopg2.connect(
            dbname="indexr",
            user="postgres",
            password=os.environ["root_db_pw"],
            host="localhost",
            port="5432",
        )
    except Exception:
        print("I am unable to connect to the database")

    cur = conn.cursor()
    for sql_statement in SEED_SQL:
        try:
            cur.execute(sql_statement)
            conn.commit()
        except Exception as e:
            logging.warning(f"error seeding tags_files: {e}")
            conn.rollback()

    conn.close()
    cur.close()    
    logging.info("'seed_tags_files' complete")
