# store files in here
files_table_create = ("""
        CREATE TABLE IF NOT EXISTS
            files (
                id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                hash varchar,
                url TEXT,
                file TEXT UNIQUE,
                filetype varchar,
                date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                date_removed timestamp
            );

        CREATE INDEX ON files (filetype);
""")

# tags are descriptors
tag_table_create = ("""
        CREATE TABLE IF NOT EXISTS
            tags (
                id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                tag_type TEXT,
                tag_name TEXT,
                tag_date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                tag_date_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                tag_date_removed timestamp WITH TIME ZONE,
                UNIQUE(tag_type, tag_name)
            );

        CREATE INDEX ON tags (tag_type);
        CREATE INDEX ON tags (tag_name);
""")

# tracks tags assigned to files
tags_files_create = ("""
        CREATE TABLE IF NOT EXISTS
            tags_files (
            id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            files_id INT,
            tags_id INT ,
            modified_by TEXT DEFAULT 'seed',
            date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            date_removed TIMESTAMP WITH TIME ZONE
            );

        CREATE INDEX ON tags_files (tags_id);
        CREATE INDEX ON tags_files (files_id);
        CREATE INDEX ON tags_files (modified_by);
""")


# QUERY LISTS FOR EXECUTION
create_table_queries = [files_table_create, tag_table_create, tags_files_create]
seed_table_queries = []