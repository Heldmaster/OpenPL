import cv2
import apriltag
import math

import numpy as np


class Platform:
    def __init__(self, tagId, tagSize, cameraMatrix, logger):
        self.detector = apriltag.Detector()
        self.tagId = tagId
        self.tagSize = tagSize
        self.cameraMatrix = cameraMatrix
        self.logger = logger

        self.fx = self.cameraMatrix[0, 0]
        self.fy = self.cameraMatrix[1, 1]
        self.cx = self.cameraMatrix[0, 2]
        self.cy = self.cameraMatrix[1, 2]


    def getInfo(self, frame):
        grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = self.detector.detect(grayFrame)

        for detection in detections:
            if detection.tag_id == self.tagId:

                pose, _, _ = self.detector.detection_pose(
                    detection,
                    (self.fx, self.fy, self.cx, self.cy),
                    self.tagSize
                )

                translation = pose[:3, 3]
                distance = np.linalg.norm(translation)

                centerX, centerY = detection.center
                angleX = math.atan((centerX - self.cx) / self.fx)
                angleY = math.atan((centerY - self.cy) / self.fy)

                return {
                    "tagId": detection.tag_id,
                    "angleX": angleX,
                    "angleY": angleY,
                    "distance": distance
                }

        return None
