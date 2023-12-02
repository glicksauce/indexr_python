#!/usr/bin/python
import psycopg2
import os

print("starting....")
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
try:
    cur.execute("Drop TABLE tags")
    conn.commit()
except Exception as e:
    print("I can't drop our test database!", e)

conn.close()
cur.close()
