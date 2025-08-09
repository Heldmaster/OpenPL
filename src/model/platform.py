import cv2
import pupil_apriltags
import math
import logging

import numpy as np
from typing import Dict, Optional


class Platform:
    def __init__(
        self,
        tagId: int,
        tagSize: float,
        cameraMatrix: np.ndarray,
        logger: logging.Logger,
    ) -> None:
        self.detector: pupil_apriltags.Detector = pupil_apriltags.Detector(
            families="tag36h11",
            nthreads=1,
            quad_decimate=1.0,
            quad_sigma=0.0,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=0,
        )
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

        detections: list[pupil_apriltags.Detection] = self.detector.detect(
            grayFrame,
            estimate_tag_pose=True,
            camera_params=(self.fx, self.fy, self.cx, self.cy),
            tag_size=self.tagSize,
        )

        for detection in detections:
            if detection.tag_id == self.tagId:
                translation: np.ndarray = detection.pose_t
                distance: float = np.linalg.norm(translation)

                centerX: float = detection.center[0]
                centerY: float = detection.center[1]
                angleX: float = math.atan((centerX - self.cx) / self.fx)
                angleY: float = math.atan((centerY - self.cy) / self.fy)

                return {
                    "tagId": detection.tag_id,
                    "angleX": angleX,
                    "angleY": angleY,
                    "distance": distance,
                }

        return None
