import json

from PIL import Image
import numpy as np


class ScreenAnimation:
	PROGRESS_BAR = 'progress_bar'
	TALK = 'talk'
	SUN = 'sun'
	CLOUDY = 'cloudy'
	RAIN = 'rain'
	STORM = 'storm'
	SNOW = 'snow'
	CHECKBOX = 'checkbox'
	SHUTDOWN = 'shutdown'
	WIFI = 'wifi'
	CLOUD_PROGRESS = 'cloud_progress'
	WARNING = 'warning'
	SONG = 'song'
	WAVES = 'waves'
	SIGNAL = 'signal'
	POINTER = 'pointer'
	BUBBLES = 'bubbles'

	ICONS = {
		'progress_bar': 'progress_bar.json',
		'talk': 'talk.json',
		'sun': 'sun.json',
		'cloudy': 'cloudy.json',
		'rain': 'rain.json',
		'storm': 'storm.json',
		'snow': 'snow.json',
		'checkbox': 'checkbox.json',
		'shutdown': 'shutdown.json',
		'wifi': 'wifi.json',
		'cloud_progress': 'cloud_progress.json',
		'warning': 'warning.json',
		'song': 'song.json',
		'waves': 'waves.json',
		'signal': 'signal.json',
		'pointer': 'pointer.json',
		'bubbles': 'bubbles.json'
	}

	@staticmethod
	def get_list():
		"""Get a list of all available screen animations."""
		return list(ScreenAnimation.ICONS.keys())

	@staticmethod
	def get_animation_path(animation: str, path: str = 'static/icons'):
		"""Get the path of a screen animation."""
		return f'{path}/{ScreenAnimation.ICONS[animation]}'

	@staticmethod
	def get(name: str):
		"""Get the JSON content of a screen animation."""
		with open(ScreenAnimation.get_animation_path(name)) as f:
			return json.load(f)

	@staticmethod
	def get_image(name: str):
		"""Get the image content of a screen animation."""
		data = ScreenAnimation.get(name)
		frames = []
		for byte_list in data:
			byte_array = bytes(byte_list)
			bits = np.unpackbits(np.frombuffer(byte_array, dtype=np.uint8))
			data = bits.reshape((64, 64))
			data *= 255
			image = Image.fromarray(data)
			frames.append(image)
		return frames
