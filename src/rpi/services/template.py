from services.service import Service


class TemplateService(Service):

	def init(self):
		"""Initialize the service."""
		pass

	def destroy(self):
		"""Destroy the service."""
		pass

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		pass

	def loop(self):
		"""Service loop."""
		pass
