import json


def load_system_configurations() -> dict:
    return json.load(open('./static/system_config.json'))