import cv2
import numpy as np
import imagezmq
import threading
from abc import ABC, abstractmethod
from typing import Optional, Dict
import time

from src.videostreaming.drawer import DebugDrawer
from src.internal.exception import ApplicationError


class VideoStreamer(ABC):
    def __init__(self, camera: "Camera", platform: "Platform"):
        self.camera = camera
        self.platform = platform

        self._debug_drawer = DebugDrawer()

        self._thread = None

        self._running = False

    def get_frame(self):
        """
        Gets frame from camera and landing platform info (ID, corners, etc)
        """
        _, frame = self.camera.getFrame()
        if self.platform is not None:
            activeInfo, cornersAll = self.platform.getInfo(self.camera)
        else:
            activeInfo = None
            cornersAll = None

        return frame, activeInfo, cornersAll

    def start(self):
        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        if not self._running:
            return

        self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join()

    @abstractmethod
    def _worker(self):
        pass


class ImageZMQStreamer(VideoStreamer):
    def __init__(self, camera: "Camera", platform: "Platform"):
        super().__init__(camera, platform)

        self.sender = None

    def start(self):
        self.sender = imagezmq.ImageSender(
            connect_to="tcp://127.0.0.1:5551", REQ_REP=False
        )  # This is for system internal use, so I've been lazy to add URI to the config
        super().start()

    def stop(self):
        self.sender.close()
        super().stop()

    def _worker(self):
        while self._running:
            frame, activeInfo, cornersAll = self.get_frame()
            cameraMatrix = self.camera.getCameraMatrix()
            processed_frame = self._debug_drawer.process_frame(
                frame, cameraMatrix, activeInfo, cornersAll
            )
            self.sender.send_image("DebugVideo", processed_frame)
            time.sleep(0.05)


class VideoStreamerFactory:
    @classmethod
    def create(
        self,
        type: str,
        camera: "Camera",
        platfrom: "Platform",
    ):
        if type == "imagezmq":
            return ImageZMQStreamer(camera, platfrom)
        else:
            raise ApplicationError(f"Unknown VideoStremer type: {type}")
