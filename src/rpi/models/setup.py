import os
import json
import logging

CONFIG_FILE_PATH = './static/config.json'
TEMP_CONFIG_FILE_PATH = './static/config.temp.json'


def load_config(path: str = CONFIG_FILE_PATH) -> dict:
	"""Load the system configuration from the file system.
	Args:
		path (str): The path to the configuration file
	Returns:
		dict: The system configuration
	"""
	if not os.path.exists(path):
		raise FileNotFoundError(f'File not found: {path}')
	with open(path, 'r', encoding='utf-8') as file:
		return json.load(file)


def save_config(config: dict, path: str = CONFIG_FILE_PATH) -> dict:
	"""Save the system configuration to the file system.
	Args:
		config (dict): The system configuration
		path (str): The path to the configuration file
	Returns:
		dict: The system configuration
	"""
	with open(path, 'w', encoding='utf-8') as file:
		json.dump(config, file, ensure_ascii=False, indent=4)
	return config


def reset_config(path: str = CONFIG_FILE_PATH, default_path: str = TEMP_CONFIG_FILE_PATH) -> dict:
	"""Reset the system configuration to the default factory settings.
	Args:
		path (str): The path to the configuration file
		default_path (str): The path to the default configuration file
	Returns:
		dict: The system configuration
	"""
	config = load_config(default_path)
	save_config(config, path)
	return config


def init_logging(debug: bool = False) -> None:
	"""Set up logging for debugging and system monitoring."""
	if not os.path.exists('logs'):
		os.makedirs('logs')
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG) if debug else logger.setLevel(logging.INFO)
	file_handler = logging.FileHandler('logs/eymo.log')
	file_handler.setLevel(logging.DEBUG) if debug else file_handler.setLevel(logging.INFO)
	file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(file_formatter)
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.DEBUG) if debug else console_handler.setLevel(logging.INFO)
	console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	console_handler.setFormatter(console_formatter)
	if not logger.handlers:
		logger.addHandler(file_handler)
		logger.addHandler(console_handler)
	else:
		logger.handlers = []
		logger.addHandler(file_handler)
		logger.addHandler(console_handler)
