import os
import subprocess
import logging

from pathlib import Path
from dotenv import load_dotenv

from services.service import Service

from models.screen_mode import ScreenMode


class NetworkService(Service):
	DEPENDENCIES = ['screen']
	LOOP_DELAY = 15

	CHECK_CONNECTION_FILE = "state/network/connected"

	def init(self):
		"""Initialize the service."""
		self.__has_internet = False

	def destroy(self):
		"""Destroy the service."""
		pass

	def is_connected(self):
		"""Check if the robot has internet connection."""
		return self.__has_internet

	def __check_connection(self):
		"""Check if the robot has internet connection."""
		if os.path.exists(self.CHECK_CONNECTION_FILE):
			if self.__has_internet == False:
				logging.debug("[NETWORK] Changing screen to standby...")
				self._services['screen'].mode(ScreenMode.STANDBY)
			self.__has_internet = True
		else:
			logging.debug("[NETWORK] Changing screen to Wifi...")
			self._services['screen'].mode(ScreenMode.WIFI)
			self.__has_internet = False

	def before(self):
		dotenv_path = Path('static/.env')
		load_dotenv(dotenv_path=dotenv_path)

		self.__ssid = str(os.getenv("WIFI_SSID"))
		self.__password = str(os.getenv("WIFI_PASSWORD"))

	def loop(self):
		"""Service loop."""
		self.__check_connection()

		if not self.__has_internet:
			logging.warning("There's no internet connection detected, trying to connect...")
			self.connect_to_wifi(self.__ssid, self.__password)

	def __scan_wifi(self):
		try:
			result = subprocess.run(['nmcli', '-t', '-f', 'SSID', 'dev', 'wifi'], check=True, stdout=subprocess.PIPE,
									stderr=subprocess.PIPE)
			networks = result.stdout.decode().split('\n')
			return [ssid.strip() for ssid in networks if ssid.strip()]
		except subprocess.CalledProcessError as e:
			logging.error(f"Error scanning for Wi-Fi networks: {e}")
			return []

	def connect_to_wifi(self, ssid: str, password: str):
		try:
			subprocess.run(['nmcli', '-v'], check=True)
		except subprocess.CalledProcessError:
			logging.warning("nmcli is not installed. Please install NetworkManager to use this script.")
			return

		available_networks = self.__scan_wifi()
		if ssid not in available_networks:
			logging.warning(f"No network with SSID '{ssid}' found.")
			return

		# Connect to the Wi-Fi network
		try:
			subprocess.run(['sudo', 'nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], check=True)
			if not os.path.exists(self.CHECK_CONNECTION_FILE):
				open(self.CHECK_CONNECTION_FILE, "w").close()
			logging.info(f"Successfully connected to {ssid}")
			self._services['screen'].mode(ScreenMode.STANDBY)
			self.__has_internet = True
		except subprocess.CalledProcessError as e:
			logging.error(f"Failed to connect to {ssid}: {e}")
