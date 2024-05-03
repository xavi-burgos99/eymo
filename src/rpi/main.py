import logging

from rpi.controllers.camera_controller import CameraController
from src.rpi.services.voice_assistant import VoiceAssistant
from src.rpi.controllers.arduino_controller import ArduinoController
from src.rpi.controllers.screen_controller import ScreenController
from src.rpi.services.server_communication import ServerCommunication
from src.rpi.utils.network_utils import check_network_connection
from src.rpi.configs.system_config import load_system_configurations


def setup_logging() -> None:
    """
    Set up logging for debugging and system monitoring.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def initialize_components() -> tuple[ArduinoController, ScreenController, ServerCommunication, VoiceAssistant, CameraController]:
    """
    Initialize all components required for the robot's operation.
    :return: Tuple of components (ArduinoController, ScreenController, ServerCommunication, VoiceAssistant)
    """
    logging.info("Loading system configurations...")
    config = load_system_configurations()

    logging.info("Initializing Arduino controller...")
    arduino = ArduinoController(config['arduino'])

    logging.info("Setting up screen controller...")
    screen = ScreenController(config['screen'])

    logging.info("Starting server communication service...")
    server_comm = ServerCommunication(config['server'])

    logging.info("Launching the voice assistant service...")
    voice_assistant = VoiceAssistant(config['voice'], server_comm)

    logging.info("Setting up camera controller service...")
    camera_controller = CameraController(config['camera'])

    return arduino, screen, server_comm, voice_assistant, camera_controller


def main():
    """
    Main function to start the robot. This function initializes all components and starts the voice assistant service.
    """
    setup_logging()

    logging.info("Checking network connection...")
    if not check_network_connection():
        logging.error("No network connection available. Please check your network settings.")
        return

    arduino, screen, server_comm, voice_assistant, camera_controller = initialize_components()

    try:
        logging.info("Robot is starting up...")
        voice_assistant.listen()
    except KeyboardInterrupt:
        logging.info("Shutting down the robot...")
    finally:
        # arduino.cleanup()
        logging.info("Robot has been shut down successfully.")


if __name__ == "__main__":
    main()
