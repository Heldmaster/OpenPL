import logging
from abc import ABC, abstractmethod

from src.model.camera import Camera, DefaultCamera, VirtualCamera
from src.internal.exception import CameraError


class CameraReader(ABC):
    @abstractmethod
    def read(self) -> Camera:
        pass


class StreamCameraReader(CameraReader):
    pass


class DefaultCameraReader(StreamCameraReader):
    def __init__(self, path: str, logger: logging.Logger) -> None:
        pass  #!

    def read(self) -> Camera:
        # parse params here #!
        return DefaultCamera()  # params here


class VirtualCameraReader(StreamCameraReader):
    def __init__(self, path: str, logger: logging.Logger) -> None:
        pass  #!

    def read(self) -> Camera:
        # parse params here #!
        return VirtualCamera()  # params here


class AbstractCameraFactory(ABC):
    @abstractmethod
    def create(self, name: str, logger: logging.Logger) -> Camera:
        pass


class StreamCameraFactory(AbstractCameraFactory):
    def __init__(self, path: str) -> None:
        self.path = path

    def create(self, name: str, logger: logging.Logger) -> Camera:
        if name == "default":
            reader = DefaultCameraReader(self.path, logger)
            return reader.read()
        elif name == "virtual":
            reader = VirtualCameraReader(self.path, logger)
            return reader.read()
        else:
            raise CameraError(f"Unknown camera type: {name}")
