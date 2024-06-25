import json
import urllib3

import requests
import logging


def get_location(ip_address: str) -> dict or None:
	try:
		url = f'https://ipapi.co/{ip_address}/json/'
		response = urllib3.PoolManager().request('GET', url)
		response = json.loads(response.data.decode('utf-8'))
		location_data = {
			"city": response.get("city"),
			"lat": response.get("latitude"),
			"long": response.get("longitude")
		}
		return location_data
	except urllib3.exceptions.HTTPError as http_err:
		logging.error(f'HTTP error occurred: {http_err}')
	except urllib3.exceptions.RequestError as err:
		logging.error(f'Error occurred: {err}')
	return None


def get_ip() -> str or None:
	try:
		"""Get the public IP address of the device in format string."""
		response = requests.get('https://api.ipify.org?format=json')
		response.raise_for_status()  # Raise an error for bad status codes
		ip_address = response.json().get('ip')
		if ip_address:
			logging.info(f"Connected with public IP address: {ip_address}")
			return ip_address
		else:
			logging.error("Failed to retrieve public IP address.")
	except requests.RequestException as err:
		logging.error(f'Error occurred while getting public IP address: {err}')
	return None
