import os
import time
import logging

from models.setup import load_config, init_logging
from models.utils import is_rpi
from services.cloud import CloudService
from services.data_manager import DataManagerService
from services.reminders import RemindersService
from services.voice_assistant import VoiceAssistantService

from services.arduino import ArduinoService
from services.network import NetworkService
from services.camera import CameraService
from services.remote import RemoteService
from services.tts import TTSService
from services.stt import STTService
from services.vision import VisionService
from services.screen import ScreenService

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def init_local_services(config: dict, services: dict):
	"""Initialize services that are going to run locally on the robot.
	Args:
		config (dict): The system configuration
		services (dict, optional): The services to initialize. Defaults to {}.
	Returns:
		dict: The initialized services
	"""
	ArduinoService('arduino', config, services)
	NetworkService('network', config, services)
	CameraService('camera', config, services)
	RemoteService('remote', config, services)
	TTSService('tts', config, services)
	STTService('stt', config, services)
	VisionService('vision', config, services)
	ScreenService('screen', config, services)
	DataManagerService('data_manager', config, services)


def init_cloud_services(config: dict, services: dict):
	"""Initialize services that are going to run on the cloud.
	Args:
		config (dict): The system configuration
		services (dict, optional): The services to initialize. Defaults to {}.
	Returns:
		dict: The initialized services
	"""
	CloudService('cloud', config, services)
	RemindersService('reminders', config, services)
	VoiceAssistantService('voice_assistant', config, services)


def main():
	"""Main function to start the EYMO robot."""

	logging.info("Loading system configurations...")
	config = load_config()

	# Initialize logging for debugging and system monitoring
	init_logging(config.get('system', {}).get('debug', False))

	# Initialize services
	services = {}

	# Initialize local services
	logging.info("Initializing local services...")
	init_local_services(config, services)

	# Initialize cloud services
	logging.info("Initializing cloud services...")
	init_cloud_services(config, services)

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
