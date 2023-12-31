import os
import logging
import psycopg2

SQL_STATEMENTS = [
    """
    INSERT INTO tags (tag_type, tag_name)
    VALUES ('user', 'hank')
    """
]


def seed_tags():
    logging.info("starting 'seed_tags'")
    try:
        conn = psycopg2.connect(
            database="indexr",
            user="postgres",
            password=os.environ["root_db_pw"],
            host="localhost",
            port="5432",
        )
    except Exception:
        print("I am unable to connect to the database")

    cur = conn.cursor()

    for sql_statement in SQL_STATEMENTS:
        try:
            cur.execute(sql_statement)
            conn.commit()
        except Exception as e:
            logging.warning(f"error inserting into seed_tags: {e}")
            conn.rollback()

    conn.close()
    cur.close()
    logging.info("'seed_tags' complete")