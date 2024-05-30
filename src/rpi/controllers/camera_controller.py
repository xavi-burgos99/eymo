import base64
import logging
import threading

import cv2
import numpy as np


class CameraController:
    def __init__(self, config: dict):
        self.cam = cv2.VideoCapture(config["cam_port"])

    def get_frame(self, base64_encode=True):
        result, image = self.cam.read()
        if not result:
            logging.error("Could not read camera image.", exc_info=True)
            return None
        if base64_encode:
            retval, buffer = cv2.imencode('.png', image)
            png_as_text = base64.b64encode(buffer)
            return png_as_text
        return image

    def record_video(self, duration):
        threading.Thread(target=self._record_video, args=(duration,)).start()

    def get_camera(self):
        return self.cam

    def _record_video(self, duration):
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
                cv2.imshow('Video', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.cam.release()
            cv2.destroyAllWindows()

        return video_frames
