#!/usr/bin/python
import datetime
import psycopg2
import psycopg2.extras
import os
from pprint import pprint
from random import randint

from .schema.schema import DBName, FilesTable, TagsFilesTable, TagsTable


class TableQueries:
    def new_conn(self):
        try:
            self.conn = psycopg2.connect(
                database=DBName.name,
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
        Gets random row from files table
        return: dict of files row data
        """
        try:
            self.new_conn()

            # count rows
            self.cur.execute(f"SELECT count(*) from {FilesTable.name}")
            # random row
            row_count = self.cur.fetchall()[0][0]
            if not row_count:
                return
            random_int = randint(0, row_count - 1)

            self.cur.execute(f"SELECT * from {FilesTable.name} offset {random_int} LIMIT 1")
            row_dict_result = [dict(row) for row in self.cur.fetchall()][0]
            pprint(f"random image pulled, file: {row_dict_result.get('file')}")
            self.close_conn()
            return row_dict_result
        except Exception as e:
            pprint("get_random_image_ref failed", e)

    def create_tag(self, kwargs):
        """
        Adds tag to `tags` table. Safe fail if tag already exists
        """
        print("kwargs are", kwargs)
        try:
            self.new_conn()

            format_coumns = ','.join([key for key in kwargs.keys()])
            format_values = ','.join([f"'{value}'" for value in kwargs.values()])
            print("format_columns", format_coumns, "format values", format_values)
            self.cur.execute(
                f"INSERT into {TagsTable.name} ({format_coumns})"
                f" VALUES ({format_values})"
                f" ON CONFLICT ({format_coumns}) DO UPDATE SET tag_name=EXCLUDED.tag_name"
                f" RETURNING id"

            )
            associated_tag_id = self.cur.fetchone()[0]
            pprint(f"tags row created, id: {associated_tag_id}")
            self.conn.commit()
            self.close_conn()
            return associated_tag_id
        except Exception as e:
            pprint("create_tag failed", e)

    def get_tags_for_image_id(self, files_id):
        """
        returns dict of tag data from :
            id:
        """
        try:
            self.new_conn()

            # tags for image
            self.cur.execute(
                f"SELECT {TagsFilesTable.name}.id, tags.tag_name, tags.id from {TagsFilesTable.name}"
                f" LEFT JOIN tags on {TagsFilesTable.name}.tags_id = tags.id"
                f" WHERE {TagsFilesTable.name}.files_id = {files_id}"
            )
            row_tags = [dict(row) for row in self.cur.fetchall()]
            pprint(f"tags for {TagsFilesTable.name} where files_id={files_id}: {row_tags}")
            self.close_conn()
            return row_tags
        except Exception as e:
            pprint("get_tags_for_image_id failed", e)

    def get_files_from_tag(self, tags_files_id):
        """
        returns dict of rows from files table :
            tags_files_id:
        """
        try:
            self.new_conn()

            # tags for image
            self.cur.execute(
                f"SELECT * from {FilesTable.name} a"
                f" LEFT JOIN {TagsFilesTable.name} b ON a.id = b.files_id"
                f" WHERE b.tags_id = {tags_files_id}"
            )
            row_tags = [dict(row) for row in self.cur.fetchall()]
            pprint(f"tag count for where tags_files_id={tags_files_id}: {len(row_tags)}")
            self.close_conn()
            return row_tags
        except Exception as e:
            pprint("get_tags_for_image_id failed", e)

    def assign_tag_to_file(self, tag_id, image_id, modified_by="user"):
        f"""
        creates entry in {TagsFilesTable.name} table, linking tag to a file:
            tag_id:
            image_id:
        """
        try:
            self.new_conn()
            # tags for image
            self.cur.execute(
                f"INSERT INTO {TagsFilesTable.name} (tags_id, files_id, modified_by)"
                f" VALUES ({tag_id}, {image_id}, '{modified_by}' )"
                f" ON CONFLICT (tags_id, files_id) DO UPDATE SET tags_id=EXCLUDED.tags_id"
                f" Returning id"
            )
            self.conn.commit()
            res = self.cur.fetchone()[0]
            pprint(f"{TagsFilesTable.name} row created, id: {res}")
            self.close_conn()
            return res
        except Exception as e:
            pprint("assign_tag_to_file failed", e)

    def update_tag_from_file(self, id, modified_by="user"):
        f"""
        updates entry in {TagsFilesTable.name} table, setting removed date:
        """
        try:
            self.new_conn()
            # tags for image
            self.cur.execute(
                f"UPDATE {TagsFilesTable.name}"
                f" SET date_removed = '{datetime.datetime.now()}', modified_by = '{modified_by}'"
                f" WHERE id = '{id}'"
                f" Returning id"
            )
            self.conn.commit()
            res = self.cur.fetchone()[0]
            pprint(f"{TagsFilesTable.name} row updated, id: {res}")

            # test delete this:
            self.cur.execute(
                f"SELECT * FROM {TagsFilesTable.name} where id = '{id}'"
            )
            pprint(f"test query:--> {self.cur.fetchall()}")
            self.close_conn()
            self.close_conn()
            return res
        except Exception as e:
            pprint("update_tag_from_file failed", e)

    def remove_tag_from_file(self, tags_id, modified_by="user"):
        f"""
        removes entry in {TagsFilesTable.name} table:
        """
        try:
            self.new_conn()
            # tags for image
            self.cur.execute(
                f"DELETE FROM {TagsFilesTable.name}"
                f" WHERE tags_id = '{tags_id}'"
                f" Returning id"
            )
            self.conn.commit()
            res = self.cur.fetchone()[0]
            pprint(f"{TagsFilesTable.name} row deleted, id: {res}")
            return res
        except Exception as e:
            pprint("remove_tag_from_file failed", e)

    def read_all_tags_files(self):
        f"""
        logs out all entries in {TagsFilesTable.name} table
        """
        try:
            self.new_conn()

            self.cur.execute(
                f"SELECT * FROM {TagsFilesTable.name} ORDER BY ID"
            )
            rows = [dict(row) for row in self.cur.fetchall()]
            pprint(f"{TagsFilesTable.name} rows:")
            for row in rows:
                pprint(row)
            self.close_conn()
        except Exception as e:
            pprint("remove_tag_from_file failed", e)


if __name__ == "__main__":
    from indexr.utils import load_creds_to_environ
    load_creds_to_environ()
    query_class = TableQueries()
    random_row = query_class.get_random_image_ref()
    # random_rows_tags_data = query_class.get_tags_for_image_id(random_row.get("id"))
    # query_class.assign_tag_to_file(3, 3)
    # query_class.read_all_tags_files()
