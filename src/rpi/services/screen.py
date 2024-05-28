import time
import threading
import logging

from services.models.vision import Vision

class Screen:
    def __init__(self, config: dict, screen_controller, camera_controller):
        self._config = config
        self._screen_controller = screen_controller
        self._screen_controller.clear()
        
        logging.info("Setting up vision module...")
        self._vision = Vision(config['vision'], camera_controller)
        
    def loop(self):
        """Main loop for the screen controller."""
        while True:
            x, y, zoom = self._vision.get_coords()
            x = ((x - 0.5) * 1.05) + 0.5
            y = ((y - 0.5) * 1.15) + 0.5
            zoom = 0.15 + (zoom * 0.5)
            self._screen_controller.standby(x, y, zoom)
            self._screen_controller.update()
            time.sleep(0.25)
        self._screen_controller.clear()
        
    def start(self):
        """Start the screen controller."""
        threading.Thread(target=self.loop).start()
        self._screen_controller.start_tkinter_loop()