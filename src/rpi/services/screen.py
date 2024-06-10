import logging
import threading

from PIL import Image, ImageDraw, ImageOps, ImageTk

from services.service import Service

from models.utils import is_rpi
from models.screen_animation import ScreenAnimation
from models.screen_mode import ScreenMode


class ScreenService(Service):
	DEPENDENCIES = ['arduino', 'camera', 'vision']

	ANIMATION_WIDTH = 64
	ANIMATION_HEIGHT = 64

	def __tk_init(self):
		"""Initializes tkinter for PCs to emulate the screen."""
		import tkinter as tk
		from tkinter import Canvas
		geometry = f'{self.__tk_width}x{self.__tk_height}'
		root = tk.Tk()
		root.title('EYMO - Emulator')
		root.geometry(geometry)
		root.resizable(False, False)
		root.lift()
		root.overrideredirect(True)
		root.config(bg='black')
		image = Image.new('1', (self.__width, self.__height), 0)
		canvas = Canvas(root, width=self.__tk_width, height=self.__tk_height, relief='ridge', highlightthickness=0)
		canvas.create_image(0, 0, anchor='nw', image=ImageTk.PhotoImage(image))
		canvas.pack()
		self.__tk_drag(root)
		self.__tk_visibility(root)
		self.__tk_root = root
		self.__tk_image = image
		self.__tk_canvas = canvas

	def __tk_clear_screen(self):
		"""Clears the tkinter screen."""
		draw = ImageDraw.Draw(self.__tk_image)
		draw.rectangle((0, 0, self.__tk_width, self.__tk_height), fill=0)

	def __tk_destroy(self):
		"""Destroys tkinter for PCs."""
		self.__tk_root.destroy()
		self.__tk_root = None
		self.__tk_canvas = None
		self.__tk_image = None
		self.__tk_is_visible = True
		self.__tk_mainloop_enabled = False

	def __tk_drag(self, root):
		coords = {"x": 0, "y": 0}

		def start_move(event, coords):
			coords["x"] = event.x
			coords["y"] = event.y

		def stop_move(event, coords):
			coords["x"] = None
			coords["y"] = None

		def dragging(event, coords, root):
			delta_x = event.x - coords["x"]
			delta_y = event.y - coords["y"]
			x = root.winfo_x() + delta_x
			y = root.winfo_y() + delta_y
			root.geometry(f"+{x}+{y}")

		root.overrideredirect(True)
		root.bind("<ButtonPress-1>", lambda event: start_move(event, coords))
		root.bind("<ButtonRelease-1>", lambda event: stop_move(event, coords))
		root.bind("<B1-Motion>", lambda event: dragging(event, coords, root))

	def __tk_visibility(self, root):
		"""Manages the visibility of the tkinter screen."""
		from pynput import keyboard
		keys = {"ctrl": False}

		def press_start(key, keys):
			if keyboard.Key.ctrl_l == key or keyboard.Key.ctrl_r == key:
				keys["ctrl"] = True
			if keys["ctrl"] and keyboard.KeyCode.from_char('h') == key:
				self.__tk_is_visible = not self.__tk_is_visible
				try:
					if self.__tk_is_visible:
						logging.info("Window visible")
						root.deiconify()
					else:
						logging.info("Window hidden")
						root.withdraw()
				except AttributeError:
					pass

		def press_end(key, keys):
			if keyboard.Key.ctrl_l == key or keyboard.Key.ctrl_r == key:
				keys["ctrl"] = False

		listener = keyboard.Listener(on_press=lambda key: press_start(key, keys),
		                             on_release=lambda key: press_end(key, keys))
		listener.start()

	def tk_mainloop(self):
		"""Starts the tkinter screen main loop."""
		if self.__tk_root is None:
			return
		self.__tk_mainloop_enabled = True
		self.__tk_root.mainloop()

	def init(self):
		"""Initializes the screen service."""
		self.__mode = ScreenMode.STARTUP
		self.__frame = 0
		self.__width = self._config.get('width', 128)
		self.__height = self._config.get('height', 64)
		self.__fps = self._config.get('fps', 23)
		self._loop_delay = 1 / self.__fps

		self.__animation = None
		self.__animation_frame = 0
		self.__animation_frames = None
		self.__animation_frames_len = None
		self.__animation_x = (self.__width - self.ANIMATION_WIDTH) // 2
		self.__animation_y = (self.__height - self.ANIMATION_HEIGHT) // 2

		padding_x = self._config.get('animation', {}).get('padding_x', 0)
		padding_y = self._config.get('animation', {}).get('padding_y', -14)
		self.__animation_x_min = padding_x
		self.__animation_x_max = self.__width - self.ANIMATION_WIDTH - padding_x
		self.__animation_x_diff = self.__animation_x_max - self.__animation_x_min
		self.__animation_x_mid = self.__animation_x_diff // 2
		self.__animation_y_min = padding_y
		self.__animation_y_max = self.__height - self.ANIMATION_HEIGHT - padding_y
		self.__animation_y_diff = self.__animation_y_max - self.__animation_y_min
		self.__animation_y_mid = self.__animation_y_diff // 2

		if not is_rpi():
			self.__scale = self._config.get('scale', 2)
			self.__tk_root = None
			self.__tk_canvas = None
			self.__tk_is_visible = True
			self.__tk_width = self.__width * self.__scale
			self.__tk_height = self.__height * self.__scale
			self.__tk_mainloop_enabled = False
			logging.info('Initializing tkinter...')
			self.__tk_init()

	def destroy(self):
		"""Destroys the screen service."""
		if not is_rpi():
			logging.info('Destroying tkinter...')
			self.__tk_destroy()
		pass

	def __select_animation(self):
		"""Selects the animation for the current mode."""
		if self.__mode == ScreenMode.STANDBY:
			self.standby()
		elif self.__mode == ScreenMode.SPEAKING:
			self.animation(ScreenAnimation.TALK)
		elif self.__mode == ScreenMode.MOVING:
			self.standby()
		elif self.__mode == ScreenMode.SUNNY:
			self.animation(ScreenAnimation.SUN)
		elif self.__mode == ScreenMode.CLOUDY:
			self.animation(ScreenAnimation.CLOUDY)
		elif self.__mode == ScreenMode.RAINY:
			self.animation(ScreenAnimation.RAIN)
		elif self.__mode == ScreenMode.STORMY:
			self.animation(ScreenAnimation.STORM)
		elif self.__mode == ScreenMode.SNOWY:
			self.animation(ScreenAnimation.SNOW)
		elif self.__mode == ScreenMode.SHUTDOWN:
			self.animation(ScreenAnimation.SHUTDOWN)
		elif self.__mode == ScreenMode.ERROR:
			self.animation(ScreenAnimation.WARNING)
		elif self.__mode == ScreenMode.MUSIC:
			self.animation(ScreenAnimation.SONG)
		elif self.__mode == ScreenMode.RECOGNIZING:
			self.animation(ScreenAnimation.WAVES)
		elif self.__mode == ScreenMode.STARTUP:
			self.animation(ScreenAnimation.PROGRESS_BAR)
		elif self.__mode == ScreenMode.WIFI:
			self.animation(ScreenAnimation.WIFI)
		elif self.__mode == ScreenMode.REMINDER:
			self.animation(ScreenAnimation.CHECKBOX)
		elif self.__mode == ScreenMode.CONNECT:
			self.animation(ScreenAnimation.SIGNAL)
		else:
			self.animation(ScreenAnimation.WARNING)

	def animation(self, name: str):
		"""Displays an animation."""
		if self.__animation == name:
			self.__animation_frame += 1
			if self.__animation_frame >= self.__animation_frames_len:
				self.__animation_frame = 0
			return
		self.__animation = name
		if is_rpi():
			self.__animation_frames = ScreenAnimation.get(name)
		else:
			self.__animation_frames = ScreenAnimation.get_image(name)
		self.__animation_frame = 0
		self.__animation_frames_len = len(self.__animation_frames)

	def standby(self):
		"""Displays the standby screen."""
		self.animation(ScreenAnimation.POINTER)

	def mode(self, mode: int):
		"""Sets the screen mode."""
		if (mode < 0 or mode > ScreenMode.last()):
			raise ValueError('Invalid screen mode')
		self.__mode = mode

	def loop(self):
		"""Main loop of the screen service."""
		self.__select_animation()
		if is_rpi():
			self.__loop_rpi()
		else:
			self.__loop_pc()
		self.__frame += 1

	def __loop_rpi(self):
		pass

	def __loop_pc(self):
		if not self.__tk_mainloop_enabled:
			return
		self.__tk_root.attributes('-topmost', True)
		canvas = self.__tk_canvas
		self.__tk_clear_screen()
		if self.__animation is not None:
			self.__calc_animation_position()
			frame = self.__animation_frames[self.__animation_frame]
			image = self.__tk_image
			image.paste(frame, (self.__animation_x, self.__animation_y))
			image = image.resize((self.__tk_width, self.__tk_height))
			image = ImageTk.PhotoImage(image)
			canvas.image = image
			canvas.create_image(0, 0, anchor='nw', image=image)
			canvas.pack()
		self.__tk_root.update()

	def __calc_animation_position(self):
		"""Calculates the animation position."""
		if self.__mode != ScreenMode.STANDBY or self._services['remote'].is_connected():
			self.__animation_x = (self.__width - self.ANIMATION_WIDTH) // 2
			self.__animation_y = (self.__height - self.ANIMATION_HEIGHT) // 2
			return
		position = self._services['vision'].get_position()
		x = position['x']
		y = position['y']
		x *= self.__animation_x_diff
		y *= self.__animation_y_diff
		self.__animation_x = int(x + self.__animation_x_min)
		self.__animation_y = int(y + self.__animation_y_min)
