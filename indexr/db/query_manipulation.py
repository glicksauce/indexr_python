#!/usr/bin/python
import psycopg2
import psycopg2.extras
import os
from pprint import pprint
from random import randint


class TableQueries:
    def new_conn(self):
        try:
            self.conn = psycopg2.connect(
                database="mydb",
                user="postgres",
                password=os.environ["root_db_pw"],
                host="localhost",
                port="5432",
            )
            self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except Exception:
            print("I am unable to connect to the database")
            raise

    def close_conn(self):
        try:
            self.conn.close()
            self.cur.close()
        except Exception:
            print("unable to close connection")
            raise

    def get_random_image_ref(self):
        """
        Gets random row from indexr table
        return: dict of indexr row data
        """
        try:
            self.new_conn()

            # count rows
            self.cur.execute("SELECT count(*) from indexr")
            # random row
            row_count = self.cur.fetchall()[0][0]
            random_int = randint(0, row_count - 1)

            self.cur.execute(f"SELECT * from indexr offset {random_int} LIMIT 1")
            row_dict_result = [dict(row) for row in self.cur.fetchall()][0]
            pprint(f"random image pulled, file: {row_dict_result.get('file')}")
            self.close_conn()
            return row_dict_result
        except Exception as e:
            pprint("get_random_image_ref failed", e)

    def get_tags_for_image_id(self, id):
        """
        returns dict of tag data from :
            id:
        """
        try:
            self.new_conn()

            # tags for image
            self.cur.execute(
                f"SELECT tagged_indexr.id, tags.tag_name, tags.id from tagged_indexr"
                f" LEFT JOIN tags on tagged_indexr.id = tags.id"
                f" WHERE tagged_indexr.indexr_id = {id}"
            )
            row_tags = [dict(row) for row in self.cur.fetchall()]
            pprint(f"tags for row {id}: {row_tags}")
            self.close_conn()
            return row_tags
        except Exception as e:
            pprint("get_tags_for_image_id failed", e)

    def assign_tag_to_file(self, tag_id, image_id, modified_by="user"):
        """
        creates entry in tagged_indexr table, linking tag to a file:
            tag_id:
            image_id:
        """
        try:
            self.new_conn()
            # tags for image
            self.cur.execute(
                f"INSERT INTO tagged_indexr (tags_id, indexr_id, modified_by)"
                f" VALUES ({tag_id}, {image_id}, '{modified_by}' )"
                f" Returning id"
            )
            self.conn.commit()
            pprint(f"tagged_indexr row created, id: {self.cur.fetchone()[0]}")
            self.close_conn()
        except Exception as e:
            pprint("assign_tag_to_file failed", e)

    def read_all_tagged_indexr(self):
        """
        logs out all entries in tagged_indexr table
        """
        try:
            self.new_conn()

            self.cur.execute(
                f"SELECT * FROM tagged_indexr ORDER BY ID"
            )
            tagged_indexr_rows = [dict(row) for row in self.cur.fetchall()]
            pprint(f"tagged_indexr_rows:")
            for row in tagged_indexr_rows:
                pprint(row)
            self.close_conn()
        except Exception as e:
            pprint("assign_tag_to_file failed", e)


test_query = TableQueries()
random_row = test_query.get_random_image_ref()
random_rows_tags_data = test_query.get_tags_for_image_id(random_row.get("id"))
test_query.assign_tag_to_file(3, 3)
test_query.read_all_tagged_indexr()
