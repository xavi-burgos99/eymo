import logging
from typing import Any

from rpi.models.location import get_ip, get_location
from rpi.services.service import Service


class DataManagerService(Service):
	LOOP_DELAY = 15

	def init(self):
		"""Initialize the service."""
		self.data = self._global_config
		self.subscribers = {}

		if 'reminders' not in self.data:
			self.data['reminders'] = []

	def destroy(self):
		"""Destroy the service."""
		self.__clear_data__()

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		self.data['ip_address'] = get_ip()

	def loop(self):
		"""Service loop."""
		if not self.data.get('ip_address'):
			self.__store_data__('ip_address', get_ip())
		self.__update_location__()
		logging.info(f"Data in DataManager: {self.data}")

	def subscribe(self, keys: list or str, on_change: callable) -> dict or any:
		"""
		Subscribe to data changes. If the key is already in the data, data is returned immediately.
		Parameters
		----------
		keys: list | str
		on_change: callable

		Returns dict | any
		-------

		"""
		if isinstance(keys, str):
			keys = [keys]

		for key in keys:
			if key not in self.subscribers:
				self.subscribers[key] = []
			self.subscribers[key].append(on_change)

		# Return the data for the requested keys
		if len(keys) == 1:
			return self.data.get(keys[0], None)
		else:
			return {key: self.data.get(key, None) for key in keys}

	def connect_mobile(self, mobile_info: dict):
		"""
		Marks the mobile as connected and stores the mobile information.
		Parameters
		----------
		mobile_info: dict

		Returns None
		-------

		"""
		logging.info(f"Mobile connected with data: {mobile_info}")
		self.__store_data__('phone', mobile_info)

	def disconnect_mobile(self):
		"""
		Marks the mobile as disconnected.
		Returns None
		-------

		"""
		logging.info("Mobile disconnected")
		self.data.pop('phone', None)

	def is_mobile_connected(self) -> bool:
		"""
		Check if the mobile is connected.
		Returns bool
		-------

		"""
		return 'phone' in self.data

	def update_data(self, key: str, value: Any):
		"""
		Update a specific key in the data dictionary.

		Parameters
		----------
		key : str
			The key to update.
		value : Any
			The new value for the key.

		Returns
		-------
		None
		"""
		self.__store_data__(key, value)

	def remove_data(self, key: str):
		"""
		Remove a specific key from the data dictionary.

		Parameters
		----------
		key : str
			The key to remove.
		"""
		self.__remove_data__(key)

	def __update_location__(self) -> dict or None:
		"""Update the location."""
		if self.is_mobile_connected() and 'location' in self.data['phone']:
			location = self.data['phone']['location']
		else:
			location = get_location(self.data.get('ip_address'))
		self.__store_data__('robot_location', location)
		return location

	def __clear_data__(self):
		"""Clear all stored data."""
		self.data.clear()
		self.__notify_all_subscribers__(self.data)
		self.subscribers.clear()

	def __store_data__(self, key: str, value: Any):
		"""Store data."""
		if key is not None and value is not None:
			self.data[key] = value
			self.__notify_subscribers__(key, value)
		else:
			logging.warning(f"Invalid data to store: {key} - {value}")

	def __remove_data__(self, key: str):
		"""Remove data."""
		if key in self.data:
			self.data.pop(key)
			self.__notify_subscribers__(key, None)
		else:
			logging.warning(f"Key not found: {key}")

	def __notify_subscribers__(self, key: str, value: Any):
		"""Notify subscribers about the data change."""
		if key in self.subscribers:
			for callback in self.subscribers[key]:
				callback(key, value)

	def __notify_all_subscribers__(self, data: dict):
		"""Notify all subscribers about the data change."""
		for key, subscribers in self.subscribers.items():
			value = data.get(key, None)
			for callback in subscribers:
				callback(key, value)
