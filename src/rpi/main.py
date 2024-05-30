import logging
import os
import threading

from rpi.controllers.camera_controller import CameraController
from services.tripod_mode import TripodMode
from services.voice_assistant import VoiceAssistant
from controllers.arduino_controller import ArduinoController
from controllers.screen_controller import ScreenController
from services.server_communication import ServerCommunication
from services.screen import Screen, ScreenMode
from services.models.vision import Vision
from utils.network_utils import check_network_connection
from configs.system_config import load_system_configurations, save_system_configurations

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def setup_logging() -> None:
    """
    Set up logging for debugging and system monitoring.
    """
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Crear el logger raíz
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Crear y configurar el FileHandler
    file_handler = logging.FileHandler('logs/eymo.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Crear y configurar el StreamHandler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Añadir los manejadores al logger raíz si no están ya añadidos
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    else:
        # Asegurarse de que los handlers no se dupliquen
        logger.handlers = []
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

def initialize_components(config, components = {}):
    logging.info("Initializing Arduino controller...")
    arduino = ArduinoController(config['arduino'])
    components['arduino'] = arduino
    
    logging.info("Setting up camera controller service...")
    camera_controller = CameraController(config['camera'])
    components['camera_controller'] = camera_controller
    
    logging.info("Starting vision service...")
    vision = Vision(config['vision'], camera_controller)
    components['vision'] = vision

    logging.info("Setting up screen controller...")
    screen_controller = ScreenController(config['screen'])
    components['screen_controller'] = screen_controller
    
    logging.info("Setting up screen service...")
    screen = Screen(config['screen'], screen_controller, vision)
    components['screen'] = screen

    logging.info("Setting up tripod mode...")
    tripod_mode = TripodMode(config['tripod_mode'])
    components['tripod_mode'] = tripod_mode

    return components

def initialize_cloud_components(config, components = {}):
    logging.info("Starting server communication service...")
    server_comm = ServerCommunication(config['server'])
    components['server_comm'] = server_comm
    
    logging.info("Launching the voice assistant service...")
    voice_assistant = VoiceAssistant(config['voice'], server_comm, screen, tripod_mode, camera_controller)

    # Update the demo mode configuration
    if config.get('voice').get('demo_mode'):
        logging.info("Demo mode was enabled. Disabling demo mode for next execution...")
        config['voice']['demo_mode'] = False
        save_system_configurations(config)

    return components


def main():
    """
    Main function to start the robot. This function initializes all components and starts the voice assistant service.
    """
    setup_logging()
    
    logging.info("Loading system configurations...")
    config = load_system_configurations()

    components = initialize_components(config)

    logging.info("Checking network connection...")
    if not check_network_connection():
        logging.error("No network connection available. Please check your network settings.")
        return

    components = initialize_cloud_components(config, components)
    
    screen = components['screen']
    voice_assistant = components['voice_assistant']
    
    screen.mode(ScreenMode.STANDBY)
    
    try:
        logging.info("Robot is starting up...")
        threading.Thread(target=voice_assistant.listen).start()
    except KeyboardInterrupt:
        logging.info("Shutting down the robot...")
    finally:
        # arduino.cleanup()
        logging.info("Robot has been shut down successfully.")

    try:
        logging.info("Starting screen loop...")
        screen.start()
    except KeyboardInterrupt:
        logging.info("Shutting down the screen controller...")

if __name__ == "__main__":
    main()
