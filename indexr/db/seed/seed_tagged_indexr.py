#!/usr/bin/python
import os
import psycopg2

print("starting....")
try:
    conn = psycopg2.connect(
        database="mydb",
        user="postgres",
        password="os.environ["root_db_pw"],
        host="localhost",
        port="5432",
    )
except Exception:
    print("I am unable to connect to the database")

cur = conn.cursor()
try:
    cur.execute(
        """
        INSERT INTO tagged_indexr (indexr_id, tags_id)
        VALUES (3, 1)
        """
    )
    cur.execute(
        """
        INSERT INTO tagged_indexr (indexr_id, tags_id)
        VALUES (1, 2)
        """
    )
    conn.commit()
except Exception as e:
    print("Error:", e)

conn.close()
cur.close()
