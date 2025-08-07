import cv2

from internal.exception import CameraError


class Camera:
    def __init__(self, cameraIndex, logger):
        self.cameraIndex = cameraIndex
        self.logger = logger
        self.cap = cv2.VideoCapture(self.cameraIndex)
        if not self.cap.isOpened():
            self.logger.error("Cannot open camera.")
            raise CameraError(f"Cannot open camera at index {self.cameraIndex}.")


    def getFrame(self):
        ret, frame = self.cap.read()
        return ret, frame


    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
