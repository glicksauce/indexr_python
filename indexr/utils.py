import os
import yaml
from urllib.parse import urlparse


def load_creds_to_environ():
    with open('./creds.yaml', 'r') as file:
        creds_dict = yaml.safe_load(file)
    for cred in creds_dict.get("creds", {}).keys():
        os.environ[cred] = creds_dict["creds"][cred]


def split_path_and_file(file_url: str):
    print("file url--->", file_url)
    parsed_url = urlparse(file_url)
    file_path = parsed_url.path
    file_name = os.path.basename(file_path)
    directory_path = os.path.dirname(file_path)
    print("file name--->", file_name)
    return directory_path, file_name


def get_tag_names_from_dict(tags: list):
    return [x.get("tag_name") for x in tags if x.get("tag_name") is not None]
