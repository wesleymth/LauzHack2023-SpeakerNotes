import datetime
import json
import os


def load_json_time_config(file_path: str, file_type: str) -> dict:
    with open(file_path, "r") as f:
        config = json.load(f)
    config_ = {}
    config_[f"{file_type}_start"] = datetime.timedelta(**config["start"])
    config_[f"{file_type}_end"] = datetime.timedelta(**config["end"])
    config_["pause_start_time"] = datetime.timedelta(**config["pause_start"])
    config_["pause_end_time"] = datetime.timedelta(**config["pause_end"])
    return config_


def remove_directory_contents(directory_path):
    if os.path.exists(directory_path):
        files = os.listdir(directory_path)
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(directory_path)
