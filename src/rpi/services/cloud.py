import logging
import os
import time
from typing import Any

import requests
from pathlib import Path
from dotenv import load_dotenv

from models.server_input import ServerIn
from services.service import Service
from models.utils import is_rpi


class CloudService(Service):
	LOOP_DELAY = 1800

	def init(self):
		"""Initialize the service."""
		self.host = self._config.get('host', "https://eymo.dzin.es:7125")
		self.endpoint = self._config.get('endpoint', "/action/perform")

		self.auth_endpoint = self._config.get("auth").get("endpoint", "/authentication")

		self.token = None

	def destroy(self):
		"""Destroy the service."""
		logging.warning("Destroy method called for Cloud service but it has nothing to destroy. Skipping...")

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		dotenv_path = Path('static/.env')
		load_dotenv(dotenv_path=dotenv_path)

		self.auth_data = {
			'username': str(os.getenv("API_USERNAME")),
			'password': str(os.getenv("API_PASSWORD")),
		}

	def loop(self):
		"""Service loop."""
		if is_rpi() and not self._services['network'].is_connected():
			return
		self.__get_token__()

	def call_server(self, action: str, params: dict) -> str | Any:
		"""
		Call the server with the given action and parameters.
		:param action: Action to be performed on the server.
		:param params: Parameters required for the action.
		:return: Response from the server.
		"""
		if is_rpi() and not self._services['network'].is_connected():
			logging.warning("No internet connection, skipping server call...")
			return None

		if not self.token:
			self.__get_token__()

		serverIn = ServerIn()
		serverIn.action = action
		serverIn.parameters = params

		logging.info(f"Calling server {self.host}{self.endpoint} with {serverIn.__dict__}...")
		for attempt in range(3):
			try:
				response = requests.get(f"{self.host}{self.endpoint}",
										json=serverIn.__dict__,
										headers={
											'Content-Type': 'application/json',
											'Authorization': f'Bearer {self.token}'
										},
										verify=False, timeout=10)
				response.raise_for_status()

				return response.json()
			except requests.exceptions.HTTPError as http_err:
				logging.error(f'HTTP error occurred: {http_err}')
				if response.status_code == 401:
					logging.info("Token might have expired, refreshing token...")
					self.__get_token__()
					if not self.token:
						break
				logging.info(f"Retrying... ({attempt + 1}/3)")
				time.sleep(1)
			except requests.exceptions.RequestException as err:
				logging.error(f'Error occurred: {err}')
				logging.warning(f"Retrying... ({attempt + 1}/3)")
				time.sleep(1)
		return None

	def __get_token__(self):
		"""
		Get the token from the server.
		:return: Token from the server.
		"""
		try:
			logging.info("Getting token from the server...")
			response = requests.post(f"{self.host}{self.auth_endpoint}",
									 headers={
										 'accept': 'application/json',
										 'Content-Type': 'application/x-www-form-urlencoded'
									 },
									 data=self.auth_data,
									 verify=False,
									 timeout=5)
			response.raise_for_status()

			self.token = response.json()['access_token']

		except requests.exceptions.HTTPError as http_err:
			logging.error(f'HTTP error occurred: {http_err}')
			self.token = None
		except requests.exceptions.RequestException as err:
			logging.error(f'Connection error occurred: {err}')
			self.token = None
		except Exception as e:
			logging.error(f'Main loop error occurred: {e}')
