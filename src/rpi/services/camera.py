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

	def loop(self):
		"""Service loop."""
		self.__last_frame = None
		gc.collect()

	def __convert_frame(self, type: int):
		"""Convert the camera frame."""
		frame = self.__last_frame
		if type == FrameType.NUMPY:
			return frame
		if type == FrameType.LIST:
			return frame.tolist()
		if type == FrameType.BYTES:
			return cv2.imencode('.jpg', frame)[1].tobytes()
		if type == FrameType.IMAGE:
			return Image.fromarray(frame)
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
