#!/usr/bin/python
import os
import psycopg2

print("starting....")
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
    cur.execute("Drop TABLE if exists tagged_indexr")
    conn.commit()
except Exception as e:
    print("I can't drop our test database!", e)

try:
    cur.execute(
        "CREATE TABLE tagged_indexr ( "
        "id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY, "
        "indexr_id INT, "
        "tags_id INT , "
        "modified_by TEXT DEFAULT 'seed', "
        "date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, "
        "date_removed TIMESTAMP WITH TIME ZONE "
        ");"
    )
    conn.commit()
    print("table created")
except Exception as e:
    print("I can't create indexr database!", e)

conn.close()
cur.close()
