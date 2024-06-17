import os

from services.service import Service

from models.screen_mode import ScreenMode


class NetworkService(Service):

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
			self._services['screen'].standby()
			self.__has_internet = True
		else:
			self._services['screen'].mode(ScreenMode.WIFI)
			self.__has_internet = False

	def loop(self):
		"""Service loop."""
		self.__check_connection()
