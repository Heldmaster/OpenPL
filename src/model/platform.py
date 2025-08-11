import cv2
import pupil_apriltags
import math
import logging
from abc import ABC, abstractmethod

import numpy as np
from typing import Dict, Optional

from src.model.camera import Camera


class Platform(ABC):
    @abstractmethod
    def getInfo(self, cam: "Camera") -> Optional[Dict[str, float]]:
        pass


class AprilTagPlatform(Platform):
    def __init__(
        self,
        tagId: int,
        tagSize: float,
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
        self.logger = logger

    def getInfo(self, cam: "Camera") -> Optional[Dict[str, float]]:
        ok, frame = cam.getFrame()
        if not ok:
            self.logger.warning("Failed to get frame from camera.")
            return None

        grayFrame: np.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        camMatrix: np.ndarray = cam.getCameraMatrix()
        fx: float = camMatrix[0, 0]
        fy: float = camMatrix[1, 1]
        cx: float = camMatrix[0, 2]
        cy: float = camMatrix[1, 2]

        detections: list[pupil_apriltags.Detection] = self.detector.detect(
            grayFrame,
            estimate_tag_pose=True,
            camera_params=(fx, fy, cx, cy),
            tag_size=self.tagSize,
        )

        for detection in detections:
            if detection.tag_id == self.tagId:
                translation: np.ndarray = detection.pose_t
                distance: float = np.linalg.norm(translation)

                centerX: float = detection.center[0]
                centerY: float = detection.center[1]
                angleX: float = math.atan((centerX - cx) / fx)
                angleY: float = math.atan((centerY - cy) / fy)
                corners: list[list[float]] = detection.corners.tolist()

                return {
                    "tagId": detection.tag_id,
                    "angleX": angleX,
                    "angleY": angleY,
                    "distance": distance,
                    "corners": corners,
                }

        return None
