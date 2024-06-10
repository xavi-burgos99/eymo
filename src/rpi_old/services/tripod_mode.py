import logging
import threading
import time


class TripodMode:
	def __init__(self, config: dict):
		self.enabled = config['enabled']
		self.fps = config['fps']
		resolution = config['resolution'].split('x')
		self.resolution = {}
		self.resolution['width'] = int(resolution[0])
		self.resolution['height'] = int(resolution[1])
		threading.Thread(target=self.loop).start()

	def toggle(self):
		self.enabled = not self.enabled
		logging.info("The tripod mode has been " + ("enabled" if self.enabled else "disabled"))
		return self.enabled

	def loop(self):
		while True:
			if self.enabled:
				pass
			else:
				pass
			time.sleep(1 / self.fps)

	def is_enabled(self):
		return self.enabled
