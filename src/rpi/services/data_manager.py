from rpi.models.location import get_ip, get_location
from rpi.services.service import Service


class DataManagerService(Service):
	LOOP_DELAY = 15

	def init(self):
		"""Initialize the service."""
		self.data = self._config.get("initial_data", {})
		self.mobile_connected = False

	def destroy(self):
		"""Destroy the service."""
		self.clear_data()

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		self.data['robot_ip'] = get_ip()

	def loop(self):
		"""Service loop."""
		if not self.data.get('robot_ip'):
			self.store_data('robot_ip', get_ip())
		self.update_location()

	def store_data(self, key, value):
		"""Almacena un valor asociado a una clave."""
		self.data[key] = value

	def retrieve_data(self, key):
		"""Recupera el valor asociado a una clave específica."""
		return self.data.get(key)

	def retrieve_all_data(self):
		"""Recupera todos los datos almacenados."""
		return self.data

	def clear_data(self):
		"""Limpia todos los datos almacenados."""
		self.data.clear()

	def connect_mobile(self, mobile_info):
		"""Registra un dispositivo móvil conectado."""
		self.mobile_connected = True
		self.store_data('mobile_info', mobile_info)

	def disconnect_mobile(self):
		"""Desconecta el dispositivo móvil."""
		self.mobile_connected = False
		self.store_data('mobile_info', None)

	def is_mobile_connected(self):
		"""Verifica si hay un dispositivo móvil conectado."""
		return self.mobile_connected

	def update_location(self) -> dict or None:
		"""Actualiza la ubicación del robot. Prioriza movil."""
		if self.mobile_connected and 'mobile_location' in self.data:
			location = self.data['mobile_location']
		else:
			location = get_location(self.data.get('robot_ip'))

		self.store_data('robot_location', location)
		return location
