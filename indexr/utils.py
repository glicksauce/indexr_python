import os
import yaml


def load_creds_to_environ():
    with open('./creds.yaml', 'r') as file:
        creds_dict = yaml.safe_load(file)
        print('creds dict', creds_dict)
    for cred in creds_dict.get("creds", {}).keys():
        os.environ[cred] = creds_dict["creds"][cred]
