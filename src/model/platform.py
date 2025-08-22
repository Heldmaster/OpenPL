import cv2
import pupil_apriltags
import threading
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
        tags: dict,
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
        self.tags = tags
        self.logger = logger

        # Assuming that the tag with the first id from dict is the biggest and it is guaranteed that detector will be able to detect it
        self.targetId: int = next(iter(self.tags))

        self._lock = threading.Lock()

    def getBestId(self, ids: list) -> int:
        visibleIds: list = [tag_id for tag_id in ids if tag_id in self.tags]

        if not visibleIds:
            return None

        bestId = min(visibleIds, key=lambda tagId: self.tags[tagId])

        return bestId

    def getInfo(
        self, cam: "Camera"
    ) -> tuple[Optional[dict[str, float]], list[tuple[int, list]]]:
        with self._lock:
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
                tag_size=self.tags[self.targetId],
            )

            tagsIds = []
            info: dict = None
            cornersAll: list[tuple[int, list]] = []

            for detection in detections:

                tagsIds.append(detection.tag_id)
                cornersAll.append((detection.tag_id, detection.corners.tolist()))

                if detection.tag_id == self.targetId:
                    pose_t: np.ndarray = detection.pose_t
                    pose_R: np.ndarray = detection.pose_R
                    distance: float = np.linalg.norm(pose_t)

                    centerX: float = detection.center[0]
                    centerY: float = detection.center[1]
                    angleX: float = math.atan((centerX - cx) / fx)
                    angleY: float = math.atan((centerY - cy) / fy)
                    corners: list[list[float]] = detection.corners.tolist()
                    yawError: float = np.degrees(math.atan2(pose_R[1, 0], pose_R[0, 0]))

                    info = {
                        "tagId": detection.tag_id,
                        "angleX": angleX,
                        "angleY": angleY,
                        "distance": distance,
                        "corners": corners,
                        "pose_t": pose_t,
                        "pose_R": pose_R,
                        "yawError": yawError,
                    }

            bestId = self.getBestId(tagsIds)
            if bestId is not None:
                self.targetId = bestId

            return info, cornersAll
