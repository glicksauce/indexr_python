#!/usr/bin/python
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
    cur.execute("Drop TABLE if exists tags")
    conn.commit()
except Exception as e:
    print("CAN'T DROP TAGS TABLE", e)

try:
    cur.execute(
        "CREATE TABLE tags ( "
        "id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY, "
        "tag_type TEXT, "
        "tag_name TEXT, "
        "tag_date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, "
        "tag_date_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, "
        "tag_date_removed timestamp WITH TIME ZONE, "
        "UNIQUE(tag_type, tag_name)"
        ");"
    )
    conn.commit()
    print("finished")
except Exception as e:
    print("I can't drop our test database!", e)

conn.close()
cur.close()
