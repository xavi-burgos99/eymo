import json
import urllib3

import socket
import logging


class Location:
	def __init__(self):
		self.location_data = None
		self.city = None

		self.ip_address = self.get_ip()

	def get_location(self):
		if self.location_data is None:
			url = f'https://ipapi.co/{self.ip_address}/json/'
			response = urllib3.PoolManager().request('GET', url)
			response = json.loads(response.data.decode('utf-8'))
			self.location_data = {
				"city": response.get("city"),
				"lat": response.get("latitude"),
				"long": response.get("longitude")
			}
		return self.location_data

	def get_ip(self):
		"""Get the IP address of the device in format string."""
		hostname = socket.gethostname()
		ip_address = socket.gethostbyname(hostname)
		logging.info(f"Connected with IP address: {ip_address}")
		return ip_address
