import cv2
import apriltag
import math
import logging

import numpy as np
from typing import Dict, Optional


class Platform:
    def __init__(self, tagId: int, tagSize: float, cameraMatrix: np.ndarray, logger: logging.Logger) -> None:
        self.detector: apriltag.Detector = apriltag.Detector()
        self.tagId = tagId
        self.tagSize = tagSize
        self.cameraMatrix = cameraMatrix
        self.logger = logger

        self.fx: float = self.cameraMatrix[0, 0]
        self.fy: float = self.cameraMatrix[1, 1]
        self.cx: float = self.cameraMatrix[0, 2]
        self.cy: float = self.cameraMatrix[1, 2]


    def getInfo(self, frame: np.ndarray) -> Optional[Dict[str, float]]:
        grayFrame: np.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections: list[apriltag.Detection] = self.detector.detect(grayFrame)

        for detection in detections:
            if detection.tag_id == self.tagId:

                pose: np.ndarray
                _, pose, _ = self.detector.detection_pose(
                    detection,
                    (self.fx, self.fy, self.cx, self.cy),
                    self.tagSize
                )

                translation: np.ndarray = pose[:3, 3]
                distance: float = np.linalg.norm(translation)

                centerX: float = detection.center[0]
                centerY: float = detection.center[1]
                angleX: float = math.atan((centerX - self.cx) / self.fx)
                angleY: float = math.atan((centerY - self.cy) / self.fy)

                return {
                    "tagId": detection.tag_id,
                    "angleX": angleX,
                    "angleY": angleY,
                    "distance": distance
                }

        return None
