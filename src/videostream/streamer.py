import cv2
import numpy as np
import imagezmq
from vidgear.gears import WriteGear
import threading
from abc import ABC, abstractmethod
from typing import Optional, TypeAlias
import time
import subprocess

from src.videostream.drawer import DebugDrawer
from src.internal.exception import ApplicationError

frameType: TypeAlias = np.ndarray
activeInfoType: TypeAlias = Optional[dict[str, float]]
cornersAllType: TypeAlias = list[tuple[int, list]]


class VideoStreamer(ABC):
    @abstractmethod
    def __init__(self, camera: "Camera", platform: "Platform") -> None:
        self.camera = camera
        self.platform = platform

    @abstractmethod
    def get_frame(self) -> np.ndarray:
        """
        Gets frame from camera and landing platform info (ID, corners, etc)
        """
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def _worker(self) -> None:
        pass

class NullStreamer(VideoStreamer):
    def __init__(self):
        pass

    def get_frame(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def _worker(self):
        pass

class ImageZMQStreamer(VideoStreamer):
    def __init__(self, camera: "Camera", platform: "Platform") -> None:
        self.camera = camera
        self.platform = platform
        self._debug_drawer = DebugDrawer()

        self._thread = None
        self._running = False

        self.sender = None

    def get_frame(self) -> np.ndarray:
        """
        Gets frame from camera and landing platform info (ID, corners, etc)
        """
        _, frame = self.camera.getFrame()
        if self.platform is not None:
            activeInfo, cornersAll = self.platform.getInfo(self.camera)
        else:
            activeInfo = None
            cornersAll = None

        cameraMatrix = self.camera.getCameraMatrix()
        processed_frame = self._debug_drawer.process_frame(
            frame, cameraMatrix, activeInfo, cornersAll
        )

        return processed_frame

    def start(self) -> None:
        self.sender = imagezmq.ImageSender(
            connect_to="tcp://127.0.0.1:5551", REQ_REP=False
        )  # This is for system internal use, so I've been lazy to add URI to the config

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.sender.close()
        if not self._running:
            return

        self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join()

    def _worker(self) -> None:
        while self._running:
            frame = self.get_frame()
            self.sender.send_image("DebugVideo", frame)
            time.sleep(0.05)


class RTSPStreamer(VideoStreamer):
    def __init__(self, camera: "Camera", platform: "Platform") -> None:
        self.camera = camera
        self.platform = platform
        self._debug_drawer = DebugDrawer()

        self._thread = None
        self._running = False

        self.writer = None

    def get_frame(self) -> np.ndarray:
        """
        Gets frame from camera and landing platform info (ID, corners, etc)
        """
        _, frame = self.camera.getFrame()
        if self.platform is not None:
            activeInfo, cornersAll = self.platform.getInfo(self.camera)
        else:
            activeInfo = None
            cornersAll = None

        cameraMatrix = self.camera.getCameraMatrix()
        processed_frame = self._debug_drawer.process_frame(
            frame, cameraMatrix, activeInfo, cornersAll
        )


        return processed_frame
    
    def start(self) -> None:
        output = "rtsp://127.0.0.1:8554/openpl"
        output_params = {
            "-vcodec":"libx264",
            "-crf": 25,
            "-preset": "ultrafast", 
            "-tune": "zerolatency", 
            "-f": "rtsp", 
            "-rtsp_transport": "udp",
        }

        self.writer = WriteGear(
            output=output, compression_mode=True, logging=True, **output_params
        )

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.writer.close()

        if not self._running:
            return

        self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join()

    def _worker(self) -> None:
        while self._running:
            frame = self.get_frame()

            self.writer.write(frame.astype(np.uint8))


class VideoStreamerFactory:
    @classmethod
    def create(
        self,
        type: str,
        camera: "Camera",
        platfrom: "Platform",
    ) -> VideoStreamer:
        if type == "null":
            return NullStreamer()
        elif type == "imagezmq":
            return ImageZMQStreamer(camera, platfrom)
        elif type == "rtsp":
            return RTSPStreamer(camera, platfrom)
        else:
            raise ApplicationError(f"Unknown VideoStremer type: {type}")
