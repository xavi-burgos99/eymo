import os
import abc
import time
import logging
import platform
import threading


class Service(metaclass=abc.ABCMeta):
	DEPENDENCIES = []
	MAX_ERRORS = 5
	MAX_ERRORS_REBOOT = -1
	ERROR_INTERVAL = 5
	LOOP_DELAY = 0.25

	def __init__(self, name: str, config: dict, services: dict = {}):
		"""Initialize the service.
		Args:
			name (str): The name of the service
			config (dict): The system configuration
			services (dict, optional): The services to use. Defaults to {}.
		"""
		# Check if the service exists
		if name in services:
			raise ValueError(f'The service {name} already exists.')

		# Service information
		self._name = name
		self._global_config = config
		self._config = config[name] if name in config else {}
		self._services = services
		self._loop_delay = self.LOOP_DELAY

		# Service status
		self.__initialized = False
		self.__init_try = 0
		self.__errors = 0

		# Service thread
		self.__thread = None

		# Set the service
		services[name] = self

	@abc.abstractmethod
	def init(self):
		"""Initialize the service."""
		raise NotImplementedError('The init method must be implemented.')

	@abc.abstractmethod
	def destroy(self):
		"""Destroy the service."""
		raise NotImplementedError('The destroy method must be implemented.')

	def __thread_execution(self):
		"""Service thread execution."""
		logging.info(f'Starting the {self._name} service thread...')

		# Call the before method
		if hasattr(self, 'before'):
			self.before()

		# Call the loop method
		if hasattr(self, 'loop'):
			if self._global_config.get('system', {}).get('debug', True):
				while True:
					self.loop()
					time.sleep(self._loop_delay)
			else:
				while True:
					try:
						self.loop()
						time.sleep(self._loop_delay)
					except KeyboardInterrupt:
						break
					except Exception as e:
						self.__errors += 1
						logging.error(f'An error occurred in the {self._name} service thread: {e}')
						if self.MAX_ERRORS_REBOOT != -1 and self.__errors >= self.MAX_ERRORS_REBOOT:
							logging.error(
								f'The {self._name} service has reached the maximum number of errors. Rebooting the robot...')
							self.__reboot()
							break
						if self.MAX_ERRORS != -1 and self.__errors >= self.MAX_ERRORS:
							logging.error(
								f'The {self._name} service has reached the maximum number of errors. Stopping the service...')
							break
						time.sleep(self.ERROR_INTERVAL)

	def __start_other_service(self):
		"""Start another service by try priority."""
		services = {k: v for k, v in self._services.items() if not v.is_initialized()}
		services = dict(sorted(services.items(), key=lambda item: item[1].__init_try))
		service = list(services.values())[0]
		self.__init_try += 1
		service.start()

	def start(self):
		"""Start the service."""

		# Check if the service has been initialized
		if self.__initialized:
			return

		# Check if all dependencies are initialized
		for dependency in self.DEPENDENCIES:
			if dependency not in self._services:
				raise ValueError(f'The service {self._name} requires the service {dependency}.')
			if not self._services[dependency].is_initialized():
				logging.info(f'The {self._name} service is waiting for the {dependency} service to start...')
				self.__start_other_service()
				return

		# Initialize the service
		logging.info(f'Starting the {self._name} service...')
		self.init()

		# Call the thread method
		if hasattr(self, 'before') or hasattr(self, 'loop'):
			self.__thread = threading.Thread(target=self.__thread_execution)
			self.__thread.start()

		# Set the service as initialized
		self.__initialized = True

		# Start other services
		services = {k: v for k, v in self._services.items() if not v.is_initialized()}
		if services:
			self.__start_other_service()

	def stop(self):
		"""Stop the service."""
		logging.info(f'Stopping the {self._name} service...')
		if self.__thread:
			self.__thread.join()
		self.destroy()
		self.__initialized = False
		self.__init_try = 0
		logging.info(f'The {self._name} service has stopped successfully.')

	def __reboot(self):
		"""Reboot the robot for Linux systems, stop all services and start the service again for other systems."""
		if platform.system() == 'Linux':
			logging.info('Rebooting the robot...')
			os.system('sudo reboot')
			return
		logging.error('Stopping all services...')
		for service in self._services.values():
			service.stop()
		logging.error('All services have been stopped.')
		self.start()

	def is_initialized(self) -> bool:
		"""Check if the service has been initialized.
		Returns:
			bool: True if the service has been initialized, False otherwise
		"""
		return self.__initialized
