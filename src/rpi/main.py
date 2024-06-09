import os
import time
import logging

from models.setup import load_config, save_config, reset_config, init_logging
from models.utils import is_rpi

from services.arduino import ArduinoService
from services.camera import CameraService
from services.remote import RemoteService
from services.tts import TTSService
from services.stt import STTService
from services.vision import VisionService
from services.screen import ScreenService

#os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("/Users/xavi/GitHub/eymo/src/rpi")


def init_local_services(config: dict, services: dict):
	"""Initialize services that are going to run locally on the robot.
	Args:
		config (dict): The system configuration
		services (dict, optional): The services to initialize. Defaults to {}.
	Returns:
		dict: The initialized services
	"""
	ArduinoService('arduino', config, services)
	CameraService('camera', config, services)
	RemoteService('remote', config, services)
	TTSService('tts', config, services)
	STTService('stt', config, services)
	VisionService('vision', config, services)
	ScreenService('screen', config, services)


def main():
	"""Main function to start the EYMO robot."""

	# Initialize logging for debugging and system monitoring
	init_logging()

	logging.info("Loading system configurations...")
	config = load_config()

	# Initialize services
	services = {}

	# Initialize local services
	logging.info("Initializing local services...")
	init_local_services(config, services)

	# Start the services
	services['arduino'].start()

	# Start the tkinter screen
	if not is_rpi():
		while True:
			try:
				logging.info("Starting tkinter screen...")
				services['screen'].tk_mainloop()
			except Exception as e:
				logging.error("An error occurred in the tkinter screen.")
				logging.error(e)
			time.sleep(1)


if __name__ == "__main__":
	main()
