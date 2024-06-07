import cv2
import logging

import numpy as np

from services.service import Service

from models.utils import is_rpi

if is_rpi():
	import tflite_runtime.interpreter as tflite
else:
	import tensorflow.lite as tflite


class VisionService(Service):

	DEPENDENCIES = ['camera']

	def __init_interpreter(self):
		"""Initializes the TensorFlow Lite interpreter."""
		self.__model_path = self._config.get('model_path', 'static/tensorflow/vision.tflite')
		interpreter = tflite.Interpreter(model_path=self.__model_path)
		interpreter.allocate_tensors()
		self.__interpreter = interpreter
		self.__input_details = interpreter.get_input_details()
		self.__output_details = interpreter.get_output_details()

	def __preprocess(self, frame):
		"""Preprocess the frame."""
		input_shape = self.__input_details[0]['shape']
		frame_resized = cv2.resize(frame, (input_shape[1], input_shape[2]))
		frame_normalized = frame_resized / 255.0
		if self.__input_details[0]['dtype'] == np.uint8:
			input_data = np.expand_dims(frame_resized, axis=0).astype(np.uint8)
		else:
			input_data = np.expand_dims(frame_normalized, axis=0).astype(np.float32)
		return input_data

	def __postprocess(self, output_data, frame_shape):
		detection_boxes = output_data[0][0]
		detection_classes = output_data[1][0]
		detection_scores = output_data[2][0]
		height, width, _ = frame_shape
		coords = []
		for i in range(len(detection_scores)):
			if detection_scores[i] > self.__threshold:
				ymin, xmin, ymax, xmax = detection_boxes[i]
				(xmin, xmax, ymin, ymax) = (xmin * width, xmax * width, ymin * height, ymax * height)
				coords.append({
					'class_id': int(detection_classes[i]),
					'score': detection_scores[i],
					'bbox': [xmin, ymin, xmax, ymax]
				})
		return coords

	def init(self):
		"""Initialize the service."""
		self.__threshold = self._config.get('threshold', 0.5)
		self.__interpreter = None
		self.__input_details = None
		self.__output_details = None
		self.__fps = self._config.get('fps', 5)
		self._loop_delay = 1 / self.__fps
		self.__position = {'x': 0.5, 'y': 0.5, 'z': 0.5}
		self.__has_position = False

	def destroy(self):
		"""Destroy the service."""
		pass

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		self.__init_interpreter()

	def loop(self):
		"""Service loop."""
		self.__position = {'x': 0.5, 'y': 0.5, 'z': 0.5}
		self.__has_position = False

	def get_position(self):
		"""Get the position of detected objects in the frame."""
		frame = self._services['camera'].get_frame()
		if frame is None or self.__has_position == True:
			return self.__position
		input_data = self.__preprocess(frame)
		self.__interpreter.set_tensor(self.__input_details[0]['index'], input_data)
		self.__interpreter.invoke()
		output_data = [self.__interpreter.get_tensor(output['index']) for output in self.__output_details]
		frame_shape = frame.shape
		coords = self.__postprocess(output_data, frame_shape)
		normalized_coords = []
		for coord in coords:
			bbox = coord['bbox']
			xmin, ymin, xmax, ymax = bbox
			normalized_coords.append({
				'class_id': coord['class_id'],
				'score': coord['score'],
				'bbox': [xmin / frame_shape[1], ymin / frame_shape[0], xmax / frame_shape[1], ymax / frame_shape[0]]
			})
		x = 0.5
		y = 0.5
		zoom = 0.5
		if len(normalized_coords) > 0:
			bbox = normalized_coords[0]['bbox']
			x = 1 - (bbox[0] + bbox[2]) / 2
			y = (bbox[1] + bbox[3]) / 2
			zoom = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
		position = {'x': x, 'y': y, 'z': zoom}
		self.__position = position
		self.__has_position = True
		return position
