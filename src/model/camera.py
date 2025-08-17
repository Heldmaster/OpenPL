import cv2
import numpy as np
import imagezmq
import logging
import threading
from typing import Tuple
from abc import ABC, abstractmethod

from src.internal.exception import CameraError


class Camera(ABC):
    @abstractmethod
    def getFrame(self) -> Tuple[bool, np.ndarray]:
        pass

    @abstractmethod
    def getCameraMatrix(self) -> np.ndarray:
        pass


class DefaultCamera(Camera):
    def __init__(
        self, cameraIndex: int, cameraMatrix: np.ndarray, logger: logging.Logger
    ) -> None:
        self.cameraIndex = cameraIndex
        self.cameraMatrix = cameraMatrix
        self.logger = logger

        self._lock = threading.Lock()

        self.cap: cv2.VideoCapture = cv2.VideoCapture(self.cameraIndex)
        if not self.cap.isOpened():
            self.logger.error("Cannot open camera.")
            raise CameraError(f"Cannot open camera at index {self.cameraIndex}.")

    def __enter__(self) -> "Camera":
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        self._del()

    def getFrame(self) -> Tuple[bool, np.ndarray]:
        with self._lock:
            ret: bool
            frame: np.ndarray
            ret, frame = self.cap.read()
            return ret, frame

    def _del(self) -> None:
        if self.cap.isOpened():
            self.cap.release()
        self.logger.info("Camera capture closed.")

    def getCameraMatrix(self) -> np.ndarray:
        return self.cameraMatrix


class ImageZMQCamera(Camera):
    def __init__(
        self, listen_uri: str, cameraMatrix: np.ndarray, logger: logging.Logger
    ) -> None:
        self.listen_uri = listen_uri
        self.cameraMatrix = cameraMatrix
        self.logger = logger

        self._lock = threading.Lock()

        try:
            self.image_hub = imagezmq.ImageHub(open_port=self.listen_uri, REQ_REP=False)
        except Exception as e:
            self.logger.error(
                f"Couldn't initialize ImageZMQ's ImageHub ({self.listen_uri})"
            )
            raise CameraError(
                f"Couldn't initialize ImageZMQ's ImageHub ({self.listen_uri}): {e}"
            )

    def __enter__(self) -> "Camera":
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        self._del()

    def getFrame(self) -> Tuple[bool, np.ndarray]:
        with self._lock:
            ret: bool
            frame: np.ndarray
            _, frame = self.image_hub.recv_image()

            # Minimal frame validation
            if frame is None or frame.size == 0:
                ret = False
            else:
                ret = True

            return ret, frame

    def _del(self) -> None:
        self.logger.info("Camera capture closed.")

    def getCameraMatrix(self) -> np.ndarray:
        return self.cameraMatrix
