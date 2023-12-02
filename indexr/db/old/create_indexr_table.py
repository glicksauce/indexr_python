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
    cur.execute("Drop TABLE if exists indexr")
    conn.commit()
except Exception as e:
    print("I can't drop our test database!", e)

###
# id: unique id increment
# hash: md5 hash of file
# url: remote location source
# file: local file location
# indexr_date_added: date file is added to table
# indexr_date_removed: date file is removed
###

try:
    cur.execute(
        "CREATE TABLE indexr ( "
        "id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY, "
        "hash varchar, "
        "url TEXT, "
        "file TEXT UNIQUE, "
        "filetype varchar, "
        "indexr_date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, "
        "indexr_date_removed timestamp "
        ");"
    )
    conn.commit()
    print("table created")
except Exception as e:
    print("I can't create indexr database!", e)

conn.close()
cur.close()
