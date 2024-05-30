import platform
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageDraw, ImageOps, ImageTk
import threading
import queue
import time
import logging
from pynput import keyboard
import numpy as np

from services.models.screen_animations import ScreenAnimations

SCREEN_ANIMATIONS = ScreenAnimations.get_list()

class ScreenController:
    ICON_WIDTH = 64
    ICON_HEIGHT = 64
    
    def __init__(self, config: dict):
        self._config = config
        self._window = None
        self._canvas = None
        self._image = None
        self._photo_image = None
        self._queue = queue.Queue()
        
        self._width = int(config["width"])
        self._height = int(config["height"])
        self._scale = int(config["scale"])
        
        self._icon = None
        self._icon_data = None
        self._icon_frame = 0
        self._icon_frames = 0
        
        self._icon_x = int((self._width - self.ICON_WIDTH) / 2)
        self._icon_y = int((self._height - self.ICON_HEIGHT) / 2)
        
        self._window_visible = True
        
        if platform.system() == 'Linux':
            self._testMode = False
            self._setOledScreen(config)
        else:
            self._testMode = True
            self._setTkinterScreen(config)
        self.clear()
            
    def _setOledScreen(self, config: dict):
        # TODO: Configurar la pantalla OLED
        pass
    
    def _setTkinterScreen(self, config: dict):
        self._window = tk.Tk()
        self._window.title("EYMO")
        width = self._width * self._scale
        height = self._height * self._scale
        geometry = f"{width}x{height}"
        self._window.geometry(geometry)
        self._window.resizable(width=False, height=False)
        self._window.lift()
        self._window.overrideredirect(True)
        self._window.config(bg='black')
        self._window_drag()
        self._window_visibility()
        self._canvas = Canvas(self._window, width=width, height=height, relief='ridge', highlightthickness=0)
        self._canvas.pack()
        self._image = Image.new("1", (self._width, self._height), 0)
        self._process_queue()
        
    def _window_drag(self):
        coords = {"x": 0, "y": 0}
        def start_move(event, coords):
            coords["x"] = event.x
            coords["y"] = event.y
        def stop_move(event, coords):
            coords["x"] = None
            coords["y"] = None
        def dragging(event, coords):
            delta_x = event.x - coords["x"]
            delta_y = event.y - coords["y"]
            x = self._window.winfo_x() + delta_x
            y = self._window.winfo_y() + delta_y
            self._window.geometry(f"+{x}+{y}")
        self._window.overrideredirect(True)
        self._window.bind("<ButtonPress-1>", lambda event: start_move(event, coords))
        self._window.bind("<ButtonRelease-1>", lambda event: stop_move(event, coords))
        self._window.bind("<B1-Motion>", lambda event: dragging(event, coords))
        
    def _window_visibility(self):
        keys = { "ctrl": False }
        def press_start(key, keys):
            if keyboard.Key.ctrl_l == key or keyboard.Key.ctrl_r == key:
                keys["ctrl"] = True
            if keys["ctrl"] and keyboard.KeyCode.from_char('h') == key:
                self._window_visible = not self._window_visible
                try:
                    if self._window_visible:
                        logging.info("Window visible")
                        self._window.deiconify()
                    else:
                        logging.info("Window hidden")
                        self._window.withdraw()
                except AttributeError:
                    pass
        def press_end(key, keys):
            if keyboard.Key.ctrl_l == key or keyboard.Key.ctrl_r == key:
                keys["ctrl"] = False
        listener = keyboard.Listener(on_press=lambda key: press_start(key, keys), on_release=lambda key: press_end(key, keys))
        listener.start()
        
    def standby(self, x = 0.5, y = 0.5, r = 0.33):
        """Draw a rectangle in the middle of the screen."""
        padding = 2
        if self._window is None:
            raise Exception("No screen available")
        if x < 0 or x > 1 or y < 0 or y > 1:
            raise Exception("Invalid coordinates")
        if r <= 0:
            raise Exception("Invalid radius")
        self._icon = None
        self._icon_data = None
        x = int(x * (self._width - padding * 2))
        y = int(y * (self._height - padding * 2))
        r = int(r * ((self._height - padding * 2) // 2))
        if x < padding + r:
            x = padding + r
        elif x > self._width - padding - r:
            x = self._width - padding - r
        if y < padding + r:
            y = padding + r
        elif y > self._height - padding - r:
            y = self._height - padding - r
        self.clear()
        draw = ImageDraw.Draw(self._image)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=255)
        
    def clear(self):
        """Clear the screen."""
        if self._window is None:
            raise Exception("No screen available")
        self._image = Image.new("1", (self._width, self._height), 0)
        
    def _resize(self, image):
        return image.resize((image.width * self._scale, image.height * self._scale))
    
    def icon(self, name: str):
        """Draw an icon on the screen."""
        if self._window is None:
            raise Exception("No screen available")
        if name == self._icon:
            self._draw_icon()
            return
        if name not in SCREEN_ANIMATIONS:
            raise Exception(f"Invalid icon name: {name}")
        data = ScreenAnimations.get(name)
        if data is None:
            raise Exception(f"Invalid icon data: {name}")
        self._icon = name
        self._icon_data = data
        self._icon_frame = 0
        self._icon_frames = len(data)
        
    def _byte_to_bits(self, byte):
        return [int(bit) for bit in f"{byte:08b}"]
        
    def _draw_icon(self):
        if self._icon_data is None:
            return
        self._icon_frame += 1
        if self._icon_frame >= self._icon_frames:
            self._icon_frame = 0
        frame = self._icon_data[self._icon_frame]
        if len(frame) != 512:
            logging.error(f"Frame size incorrect: {len(frame)} bytes")
            return
        data = np.array([self._byte_to_bits(byte) for byte in frame], dtype=np.uint8).reshape((64, 64))
        self.clear()
        draw = ImageDraw.Draw(self._image)
        for y, row in enumerate(data):
            for x, bit in enumerate(row):
                if bit:
                    draw.point((x + self._icon_x, y + self._icon_y), fill=255)
    
    def update(self):
        """Update the screen with the current image."""
        if self._window is None:
            raise Exception("No screen available")
        if self._testMode:
            self._queue.put(self._update_canvas)
            self._window.attributes("-topmost", True)
        else:
            pass

    def _update_canvas(self):
        """Actualiza el canvas con la imagen actual."""
        self._canvas.delete("all")
        resized_image = self._resize(self._image)
        self._photo_image = ImageTk.PhotoImage(resized_image)
        self._canvas.create_image(0, 0, anchor=tk.NW, image=self._photo_image)
        self._window.update_idletasks()

    def _process_queue(self):
        """Procesa las tareas en la cola."""
        try:
            while True:
                task = self._queue.get_nowait()
                task()
        except queue.Empty:
            pass
        self._window.after(100, self._process_queue)

    def start_tkinter_loop(self):
        """Inicia el bucle principal de tkinter"""
        if self._testMode:
            self._window.mainloop()