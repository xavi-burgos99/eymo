import numpy as np
from PIL import Image
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

class OledDisplay:
	def __init__(self, address: int = 0x3c, i2c_bus: int = 1):
		"""Initializes the OLED display."""
		serial = i2c(port=i2c_bus, address=address)
		self.__display = ssd1306(serial)

	def image(self, image: Image):
		"""Displays an image on the OLED display.
		Args:
			image (Image): The image to display
		"""
		if image.mode != '1':
			image = image.convert('1')
		with canvas(self.__display) as draw:
			draw.bitmap((0, 0), image, fill="white")

	def clear(self):
		"""Clears the OLED display."""
		self.__display.clear()
