import os
import yaml
from urllib.parse import urlparse


def load_creds_to_environ():
    with open('./creds.yaml', 'r') as file:
        creds_dict = yaml.safe_load(file)
    for cred in creds_dict.get("creds", {}).keys():
        os.environ[cred] = creds_dict["creds"][cred]


def split_path_and_file(file_url: str):
    parsed_url = urlparse(file_url)
    file_path = parsed_url.path
    file_name = os.path.basename(file_path)
    directory_path = os.path.dirname(file_path)
    return directory_path, file_name
