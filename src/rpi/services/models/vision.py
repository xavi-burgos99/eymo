import cv2
import numpy as np

#try:
#    import tflite_runtime.interpreter as tflite
#except ImportError:
#    import tensorflow.lite as tflite

import tensorflow.lite as tflite

class Vision:
  
    def __init__(self, config, camera_controller):
        self._config = config
        self._threshold = config.get('threshold', 0.5)
        self._camera_controller = camera_controller
        self._interpreter = tflite.Interpreter(model_path=config['model_path'])
        self._interpreter.allocate_tensors()
        self.input_details = self._interpreter.get_input_details()
        self.output_details = self._interpreter.get_output_details()
    
    def get_frame(self) -> np.ndarray:
        return self._camera_controller.get_frame(False)

    def _preprocess(self, frame):
        input_shape = self.input_details[0]['shape']
        frame_resized = cv2.resize(frame, (input_shape[1], input_shape[2]))
        frame_normalized = frame_resized / 255.0
        if self.input_details[0]['dtype'] == np.uint8:
            input_data = np.expand_dims(frame_resized, axis=0).astype(np.uint8)
        else:
            input_data = np.expand_dims(frame_normalized, axis=0).astype(np.float32)
        return input_data

    def _postprocess(self, output_data, frame_shape):
        detection_boxes = output_data[0][0]
        detection_classes = output_data[1][0]
        detection_scores = output_data[2][0]

        height, width, _ = frame_shape

        coords = []
        for i in range(len(detection_scores)):
            if detection_scores[i] > self._threshold:
                ymin, xmin, ymax, xmax = detection_boxes[i]
                (xmin, xmax, ymin, ymax) = (xmin * width, xmax * width, ymin * height, ymax * height)
                coords.append({
                    'class_id': int(detection_classes[i]),
                    'score': detection_scores[i],
                    'bbox': [xmin, ymin, xmax, ymax]
                })
        return coords

    def get_coords(self):
        """Get the coordinates of detected objects in the frame.
        Returns:
            (x, y, zoom) Center coordinates of detected objects, and the distance (between 0 and 1, representing between 0 or 10 meters).
        """
        frame = self.get_frame()
        input_data = self._preprocess(frame)
        self._interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self._interpreter.invoke()
        output_data = [self._interpreter.get_tensor(output['index']) for output in self.output_details]
        frame_shape = frame.shape
        coords = self._postprocess(output_data, frame_shape)
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
        return x, y, zoom
