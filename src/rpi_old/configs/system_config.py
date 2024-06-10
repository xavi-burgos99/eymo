import json

file_path = './static/system_config.json'


def load_system_configurations() -> dict:
	with open(file_path, 'r', encoding='utf-8') as file:
		return json.load(file)


def save_system_configurations(config: dict):
	with open(file_path, 'w', encoding='utf-8') as file:
		json.dump(config, file, ensure_ascii=False, indent=4)
