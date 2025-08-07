import cv2
import numpy as np
import logging
from typing import Tuple

from src.internal.exception import CameraError


class Camera:
    def __init__(self, cameraIndex: int, logger: logging.Logger) -> None:
        self.cameraIndex = cameraIndex
        self.logger = logger
        self.cap: cv2.VideoCapture = cv2.VideoCapture(self.cameraIndex)
        if not self.cap.isOpened():
            self.logger.error("Cannot open camera.")
            raise CameraError(f"Cannot open camera at index {self.cameraIndex}.")

    def getFrame(self) -> Tuple[bool, np.ndarray]:
        ret: bool
        frame: np.ndarray
        ret, frame = self.cap.read()
        return ret, frame

    def __del__(self) -> None:
        if self.cap.isOpened():
            self.cap.release()
