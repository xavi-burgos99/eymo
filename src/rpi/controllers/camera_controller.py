import logging
from typing import Any

import cv2
import numpy as np


class CameraController:
    def __init__(self, config: dict):
        self.cam = cv2.VideoCapture(config["cam_port"])

    def get_frame(self) -> None or np.ndarray:
        result, image = self.cam.read()
        if not result:
            logging.error("Could not read camera image.", exc_info=True)
            return None
        return image

    def record_video(self, duration):
        # TODO: Revisar este codigo
        if not self.cam.isOpened():
            logging.error("Cannot open camera")
            return None

        fps = self.cam.get(cv2.CAP_PROP_FPS)
        num_frames = int(fps * duration)
        video_frames = []

        try:
            for _ in range(num_frames):
                ret, frame = self.cam.read()
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break
                video_frames.append(frame)
        finally:
            self.cam.release()

        return video_frames

    def get_camera(self):
        return self.cam
