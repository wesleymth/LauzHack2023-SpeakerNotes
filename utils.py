import datetime
import json


def load_json_time_config(file_path: str, file_type: str) -> dict:
    with open(file_path, "r") as f:
        config = json.load(f)
    config_ = {}
    config_[f"{file_type}_start"] = datetime.timedelta(**config["start"])
    config_[f"{file_type}_end"] = datetime.timedelta(**config["end"])
    config_["pause_start_time"] = datetime.timedelta(**config["pause_start"])
    config_["pause_end_time"] = datetime.timedelta(**config["pause_end"])
    return config_
