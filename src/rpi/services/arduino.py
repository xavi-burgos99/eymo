import json
import serial
import logging

from services.service import Service

from models.utils import is_rpi
from models.control_mode import ControlMode

class ArduinoService(Service):

	def init(self):
		"""Initialize the service."""
		self.__port = self._config.get('port', '/dev/ttyUSB0')
		self.__baudrate = self._config.get('baudrate', 9600)
		self.__serial = None
		self.__control_mode = ControlMode.OFF

		self.__position_config = self._global_config.get('vision', {}).get('position', {})
		self.__position_zoom = self.__position_config.get('zoom_init', 0.5)
		self.__position_zoom_offset = self.__position_config.get('zoom_offset', 0.1)
		self.__position_zoom_min = self.__position_config.get('zoom_min', 0.1)
		self.__position_zoom_max = self.__position_config.get('zoom_max', 0.9)
		self.__position_horizontal_offset = self.__position_config.get('horizontal_offset', 0.1)
		self.__position_horizontal_limit = self.__position_config.get('horizontal_limit', 0.1)

	def destroy(self):
		"""Destroy the service."""
		if self.__serial is not None and self.__serial.is_open:
			self.__serial.close()
		self.__serial = None

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		if not is_rpi():
			logging.warning('The Arduino service is only available on the Raspberry Pi.')
		else:
			self.__serial = serial.Serial(self.__port, self.__baudrate)
			if not self.__serial.is_open:
				logging.error('Failed to open the Arduino serial.')
				return
			logging.info(f'Arduino serial opened on port {self.__port} with baudrate {self.__baudrate}.')
		self.send({'mode': self.__control_mode})

	def loop(self):
		"""Service loop."""
		if not is_rpi():
			return
		if self.__serial is None or not self.__serial.is_open:
			logging.error('The Arduino serial is not open.')
			return
		if self.__serial.in_waiting > 0:
			line = self.__serial.readline().decode('utf-8').strip()
			try:
				data = json.loads(line)
				logging.info(f"Received from Arduino: {data}")
			except json.JSONDecodeError:
				logging.error("Failed to decode JSON from Arduino")
		if self.__control_mode != ControlMode.TRIPOD and self.__control_mode != ControlMode.AUTO:
			return
		position = self._services['vision'].get_position()
		if position is None:
			return

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

	def mode(self, mode: int):
		"""Set the control mode."""
		if mode < 0 or mode > ControlMode.last():
			logging.error(f"Invalid control mode: {mode}")
			return
		self.__control_mode = mode
		mode = ControlMode.get_name(mode)
		logging.info(f"Arduino control mode set to {mode}")

	def get_mode(self) -> int:
		"""Get the control mode."""
		return self.__control_mode