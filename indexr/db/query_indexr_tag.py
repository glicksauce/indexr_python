#!/usr/bin/python
import os
import psycopg2

try:
    conn = psycopg2.connect(
        database="mydb",
        user="postgres",
        password=os.environ["root_db_pw"],
        host="localhost",
        port="5432",
    )
except Exception:
    print("I am unable to connect to the database")

cur = conn.cursor()

try:
    cur.execute("SELECT indexr_id from tagged_indexr WHERE indexr_id = 2")
    res1 = cur.fetchall()
    print("re1", res1)
    cur.execute(
        "SELECT tagged_indexr.id, indexr.file from tagged_indexr LEFT JOIN indexr on indexr_id = indexr.id WHERE tagged_indexr.indexr_id = 3"
    )
    res = cur.fetchall()
    print("res", res)
except Exception as e:
    print("I can't create indexr database!", e)

conn.close()
cur.close()
