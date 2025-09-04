import logging
from abc import ABC, abstractmethod
import numpy as np

from src.model.camera import Camera, DefaultCamera, ImageZMQCamera, RTSPCamera
from src.internal.exception import CameraError


class AbstractCameraFactory(ABC):
    @abstractmethod
    def create(self, name: str, logger: logging.Logger) -> Camera:
        pass


class StreamCameraFactory(AbstractCameraFactory):
    @classmethod
    def create(
        self, type: str, logger: logging.Logger, camera_matrix: np.ndarray, config: dict
    ) -> Camera:
        if type == "default":
            return DefaultCamera(config["camera"]["index"], camera_matrix, logger)
        elif type == "imagezmq":
            return ImageZMQCamera(
                config["camera"]["imagezmq_listen_uri"], camera_matrix, logger
            )
        elif type == "rtsp":
            return RTSPCamera(
                config["camera"]["rtsp_url"], camera_matrix, logger
            )
        else:
            raise CameraError(f"Unknown camera type: {type}")
