import os
import json
import time
import base64
import socket
import logging
import platform
import threading
import subprocess
from collections import deque

from services.service import Service

from models.screen_mode import ScreenMode
from models.frame_type import FrameType
from models.control_mode import ControlMode


class RemoteService(Service):
	DEPENDENCIES = ['camera', 'screen']
	LOOP_DELAY = 0.01

	def __force_close_port(self, port: int):
		"""Forces the close of a port.
		Args:
			port (int): The port to close
		"""
		system = platform.system()
		try:
			if system == "Linux" or system == "Darwin":
				result = subprocess.run(["lsof", "-t", f"-i:{port}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
				pids = result.stdout.strip().split("\n")
				if pids:
					for pid in pids:
						if pid:
							logging.info(f"Terminating process {pid} using port {port}")
							os.kill(int(pid), 9)
					logging.info(f"Port {port} is now free.")
				else:
					logging.info(f"No process found using port {port}.")
			elif system == "Windows":
				result = subprocess.run(["netstat", "-ano"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
				lines = result.stdout.strip().split("\n")
				for line in lines:
					if f":{port}" in line:
						parts = line.split()
						pid = parts[-1]
						logging.info(f"Terminating process {pid} using port {port}")
						subprocess.run(["taskkill", "/PID", pid, "/F"])
						logging.info(f"Port {port} is now free.")
						break
				else:
					logging.info(f"No process found using port {port}.")
			else:
				logging.info(f"Unsupported platform: {system}")
		except Exception as e:
			logging.info(f"Failed to close port {port}: {e}")

	def __wait_for_port_release(self, port: int):
		"""Waits for a port to be released.
		Args:
			port (int): The port to wait for
			timeout (int, optional): The timeout in seconds. Defaults to 10.
		"""
		logging.info(f'Waiting for the port {port} to be released...')
		start = time.time()
		while time.time() - start < self.__port_release_timeout:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				sock.bind((self.__host, port))
				return
			except OSError:
				time.sleep(1)
			finally:
				sock.close()
		raise TimeoutError(f'The port {port} was not released in time.')

	def __init_socket(self):
		"""Initializes the video stream."""
		self._services['screen'].mode(ScreenMode.CONNECT)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.bind((self.__host, self.__port))
		except OSError:
			self.__force_close_port(self.__port)
			self.__wait_for_port_release(self.__port)
			sock.bind((self.__host, self.__port))
		sock.settimeout(self.__socket_timeout)
		self.__sock = sock
		self._services['screen'].mode(ScreenMode.STANDBY)
		threading.Thread(target=self.__main_loop, daemon=True).start()

	def __main_loop(self):
		"""Stream loop."""
		sock = self.__sock
		while True:
			logging.info('Waiting for stream connection...')
			sock.listen(1)
			try:
				conn, addr = sock.accept()
			except socket.timeout:
				logging.info('The stream connection timed out.')
				if self.__socket_timeout_delay > 0:
					time.sleep(self.__socket_timeout_delay)
				continue
			logging.info('Stream connected.')
			self.__stream_frame = 0
			self.__stream_frame_timestamp = None
			self.__stream_connected = True
			debug_interval = 1 / self._loop_delay
			buffer = ""
			self.__on_connect()
			with conn:
				conn.settimeout(self.__socket_timeout_delay)
				while not self.__force_socket_close:
					try:
						# Receive control data
						try:
							control_data = conn.recv(4096)
							if control_data:
								buffer += control_data.decode('utf-8')
								messages = buffer.split('\n')
								buffer = messages.pop()  # Keep the incomplete message in buffer
								for message in messages:
									if message:
										try:
											control_dict = json.loads(message)
											self.__control_buffer.append(control_dict)
											self.__control(control_dict)
										except json.JSONDecodeError:
											logging.error(f"Failed to decode control data: {message}")
						except socket.timeout:
							pass
						except Exception as e:
							pass

						# Prepare data to send
						data = {}
						if self.__send_data is not None:
							data.update(self.__send_data)
							self.__send_data = None

						# Prepare image data
						mode = self._services['arduino'].get_mode()
						if mode == ControlMode.OFF or mode == ControlMode.MANUAL:
							frame = self._services['camera'].get_frame(FrameType.BYTES)
							if frame is not None:
								frame_base64 = base64.b64encode(frame).decode('utf-8')
								data['image'] = frame_base64

						# Send data
						if True:
							data_json = json.dumps(data)
							data_bytes = data_json.encode('utf-8')

							frame_size = len(data_bytes)
							conn.sendall(frame_size.to_bytes(4, byteorder='big'))
							conn.sendall(data_bytes)

						if self._global_config.get('system', {}).get('debug', True):
							if self.__stream_frame % debug_interval == 0:
								now = time.time()
								if self.__stream_frame_timestamp is not None:
									fps = debug_interval / (now - self.__stream_frame_timestamp)
									print(f'Camera Stream - FPS: {fps:.2f}')
								self.__stream_frame_timestamp = now
						self.__stream_frame += 1
					except BrokenPipeError:
						break
					except Exception as e:
						continue
					time.sleep(self._loop_delay)
			self.__on_disconnect()
			self.__stream_connected = False
			logging.info('Stream disconnected.')
			time.sleep(self.__disconnect_delay)

	def init(self):
		"""Initialize the service."""
		self._loop_delay = self._config.get('loop', self.LOOP_DELAY)

		self.__stream_connected = False
		self.__stream_frame = 0
		self.__stream_frame_timestamp = None
		self.__control_buffer = deque(maxlen=20)
		self.__send_data = None
		self.__host = self._config.get('host', self._config.get('host', '0.0.0.0'))
		self.__port = self._config.get('port', self._config.get('port', 8000))
		self.__sock = None
		self.__force_socket_close = False

		self.__port_release_timeout = self._config.get('port_release_timeout', 60)
		self.__socket_timeout = self._config.get('socket_timeout', 30)
		self.__socket_timeout_delay = self._config.get('socket_timeout_delay', 0)
		self.__disconnect_delay = self._config.get('disconnect_delay', 0)

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		self.__init_socket()

	def destroy(self):
		"""Destroy the service."""
		self.__force_socket_close = True
		if self.__sock is not None:
			self.__sock.close()
			self.__sock = None
		self.__force_socket_close = False

	def is_connected(self) -> bool:
		"""Check if the service is connected.
		Returns:
			bool: True if the service is connected
		"""
		return self.__stream_connected

	def __control(self, data: dict):
		"""Control the service.
		Args:
			data (dict): The control data
		"""
		if 'joystick' in data or 'mode' in data:
			data_ = {}
			if 'mode' in data:
				self._services['arduino'].mode(data['mode'])
				data_['mode'] = data['mode']
			if 'joystick' in data:
				mode = self._services['arduino'].get_mode()
				if mode == ControlMode.MANUAL:
					x = (data['joystick']['x'] - 0.5) * 2
					y = (data['joystick']['y'] - 0.5) * -2
					x = round(x, 2)
					y = round(y, 2)
					data_['displacement'] = {'x': x, 'y': y}
			if data_ != {}:
				self._services['arduino'].send(data_)

	def __on_connect(self):
		"""On connect event."""
		mode = self._services['arduino'].get_mode()
		self.send({'mode': mode})

	def __on_disconnect(self):
		"""On disconnect event."""
		pass

	def send(self, data: dict):
		"""Send data to the remote service."""
		if not self.__stream_connected:
			logging.warning('The stream is not connected.')
			return
		logging.info(f'Send data to the stream: {data}')
		self.__send_data = data