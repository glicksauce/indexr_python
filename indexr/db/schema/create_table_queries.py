from .schema import FilesTable, TagsFilesTable, TagsTable

files_table_create = (f"""
        CREATE TABLE IF NOT EXISTS
            {FilesTable.name} (
                id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                hash varchar,
                url TEXT,
                file TEXT UNIQUE,
                filetype varchar,
                date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                date_removed timestamp
            );

        CREATE INDEX ON {FilesTable.name} (filetype);
""")

# tags are descriptors
tag_table_create = (f"""
        CREATE TABLE IF NOT EXISTS
            {TagsTable.name} (
                id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                tag_type TEXT,
                tag_name TEXT,
                tag_date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                tag_date_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                tag_date_removed timestamp WITH TIME ZONE,
                UNIQUE(tag_type, tag_name)
            );

        CREATE INDEX ON {TagsTable.name} (tag_type);
        CREATE INDEX ON {TagsTable.name} (tag_name);
""")

# tracks tags assigned to files
tags_files_create = (f"""
        CREATE TABLE IF NOT EXISTS
            {TagsFilesTable.name} (
            id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            files_id INT,
            tags_id INT,
            UNIQUE (files_id, tags_id),
            modified_by TEXT DEFAULT 'seed',
            date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            date_removed TIMESTAMP WITH TIME ZONE
            );

        CREATE INDEX ON {TagsFilesTable.name} (tags_id);
        CREATE INDEX ON {TagsFilesTable.name} (files_id);
        CREATE INDEX ON {TagsFilesTable.name} (modified_by);
""")


# QUERY LISTS FOR EXECUTION
create_table_queries = [files_table_create, tag_table_create, tags_files_create]
seed_table_queries = []
