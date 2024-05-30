import time
import threading
import logging

from services.models.vision import Vision
from services.models.screen_animations import ScreenAnimations
from services.models.weather_types import WeatherType

class ScreenMode:
    STANDBY = 0
    SPEAKING = 1
    MOVING = 2
    WEATHER = 3
    SHUTDOWN = 4
    ERROR = 5
    MUSIC = 6
    RECOGNIZING = 7
    STARTUP = 8
    WIFI = 9
    REMINDER = 10

class Screen:
    def __init__(self, config: dict, screen_controller, vision: Vision):
        self._config = config
        self._screen_controller = screen_controller
        self._screen_controller.clear()
        
        self._mode = ScreenMode.STARTUP
        self._weather_type = WeatherType.SUNNY
        
        self._vision = vision
        
    def loop(self):
        """Main loop for the screen controller."""
        while True:
            if self._mode == ScreenMode.STANDBY:
                self.standby()
            elif self._mode == ScreenMode.MOVING:
                self.standby()
            elif self._mode == ScreenMode.WEATHER:
                self.weather(self._weather_type)
            elif self._mode == ScreenMode.SHUTDOWN:
                self.icon('SHUTDOWN')
            elif self._mode == ScreenMode.ERROR:
                self.icon('WARNING')
            elif self._mode == ScreenMode.MUSIC:
                self.icon('SONG')
            elif self._mode == ScreenMode.RECOGNIZING:
                self.icon('WAVES')
            elif self._mode == ScreenMode.SPEAKING:
                self.icon('TALK')
            elif self._mode == ScreenMode.WIFI:
                self.icon('WIFI')
            elif self._mode == ScreenMode.STARTUP:
                self.icon('PROGRESS_BAR')
            elif self._mode == ScreenMode.REMINDER:
                self.icon('CHECKBOX')
            else:
                raise ValueError(f"Invalid screen mode: {self._mode}")
            self._screen_controller.update()
            time.sleep(0.1)
        self._screen_controller.clear()
        
    def standby(self):
        x, y, zoom = self._vision.get_coords()
        x = ((x - 0.5) * 1.05) + 0.5
        y = ((y - 0.5) * 1.15) + 0.5
        zoom = 0.15 + (zoom * 0.5)
        self._screen_controller.standby(x, y, zoom)
        
    def icon(self, icon):
        self._screen_controller.icon(icon)
        
    def mode(self, mode):
        self._mode = mode
        
    def weather(self, type):
        if type == WeatherType.SUNNY:
            self.icon('SUN')
        elif type == WeatherType.CLOUDY:
            self.icon('CLOUD')
        elif type == WeatherType.RAINY:
            self.icon('RAIN')
        elif type == WeatherType.STORMY:
            self.icon('STORM')
        elif type == WeatherType.SNOWY:
            self.icon('SNOW')
        
    def start(self):
        """Start the screen controller."""
        threading.Thread(target=self.loop).start()
        self._screen_controller.start_tkinter_loop()