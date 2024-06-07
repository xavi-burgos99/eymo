import json
import serial
import logging

from services.service import Service

from models.utils import is_rpi

class ArduinoService(Service):

	def init(self):
		"""Initialize the service."""
		self.__port = self._config.get('port', '/dev/ttyUSB0')
		self.__baudrate = self._config.get('baudrate', 9600)
		self.__serial = None

	def destroy(self):
		"""Destroy the service."""
		if self.__serial is not None and self.__serial.is_open:
			self.__serial.close()
		self.__serial = None

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		if not is_rpi():
			logging.warning('The Arduino service is only available on the Raspberry Pi.')
			return
		self.__serial = serial.Serial(self.__port, self.__baudrate)

	def loop(self):
		"""Service loop."""
		if not is_rpi():
			return
		if self.__serial is not None and self.__serial.is_open:
			if self.__serial.in_waiting > 0:
				line = self.__serial.readline().decode('utf-8').strip()
				try:
					data = json.loads(line)
					logging.info(f"Received from Arduino: {data}")
				except json.JSONDecodeError:
					logging.error("Failed to decode JSON from Arduino")
		else:
			logging.error('The Arduino serial is not open.')

	def send(self, data: dict):
		"""Send data to the Arduino."""
		if not is_rpi():
			if self._global_config.get('system', {}).get('debug', True):
				logging.info(f'Send data to the Arduino: {data}')
			return
		if self.__serial is None or not self.__serial.is_open:
			logging.error('The Arduino serial is not open.')
			return
		try:
			json_data = json.dumps(data)
			self.__serial.write(json_data.encode('utf-8'))
			self.__serial.write(b'\n')
		except Exception as e:
			logging.error(f"Failed to send data to Arduino: {e}")