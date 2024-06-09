import gc
import cv2
from PIL import Image

from services.service import Service
from models.frame_type import FrameType


class CameraService(Service):

	def init(self):
		"""Initialize the service."""
		self.__camera = None
		self.__resolution = self._config.get('resolution', [512, 288])
		self.__last_frame = None
		self.__last_frame_list = None
		self.__last_frame_bytes = None
		self.__last_frame_image = None
		self.__fps = self._config.get('fps', 23)
		self._loop_delay = 1 / self.__fps

	def destroy(self):
		"""Destroy the service."""
		if self.__camera is not None:
			self.__camera.release()
			self.__camera = None

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		self.__camera = cv2.VideoCapture(self._config.get('camera', 0))
		if not self.__camera.isOpened():
			raise RuntimeError("Could not open camera")

	def loop(self):
		"""Service loop."""
		self.__last_frame = None
		self.__last_frame_list = None
		self.__last_frame_bytes = None
		self.__last_frame_image = None

	def __convert_frame(self, type: int):
		"""Convert the camera frame."""
		frame = self.__last_frame
		if frame is None:
			return None
		if type == FrameType.NUMPY:
			return frame
		if type == FrameType.LIST:
			if self.__last_frame_list is None:
				self.__last_frame_list = frame.tolist()
			return self.__last_frame_list
		if type == FrameType.BYTES:
			if self.__last_frame_bytes is None:
				self.__last_frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
			return self.__last_frame_bytes
		if type == FrameType.IMAGE:
			if self.__last_frame_image is None:
				self.__last_frame_image = Image.fromarray(frame)
			return self.__last_frame_image
		return None

	def get_frame(self, type: int = FrameType.NUMPY):
		"""Get the camera frame."""
		frame = self.__last_frame
		if frame is not None:
			return self.__convert_frame(type)
		if self.__camera is None:
			return None
		ret, frame = self.__camera.read()
		if not ret:
			return None
		frame = cv2.resize(frame, tuple(self.__resolution))
		self.__last_frame = frame
		return self.__convert_frame(type)