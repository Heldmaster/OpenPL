import logging
import math
import threading
from abc import ABC, abstractmethod
from typing import Dict, Optional

import cv2
import numpy as np
import pupil_apriltags
from src.model.camera import Camera


class Platform(ABC):
    @abstractmethod
    def get_info(self, cam: "Camera") -> Optional[Dict[str, float]]:
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

    def get_best_id(self, ids: list) -> int:
        visible_ids: list = [tag_id for tag_id in ids if tag_id in self.tags]

        if not visible_ids:
            return None

        best_id = min(visible_ids, key=lambda tag_id: self.tags[tag_id])

        return best_id

    def get_info(
        self, cam: "Camera"
    ) -> tuple[Optional[dict[str, float]], list[tuple[int, list]]]:
        with self._lock:
            ok, frame = cam.get_frame()
            if not ok:
                self.logger.warning("Failed to get frame from camera.")
                return None

            gray: np.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cam_matrix: np.ndarray = cam.get_camera_matrix()
            fx: float = cam_matrix[0, 0]
            fy: float = cam_matrix[1, 1]
            cx: float = cam_matrix[0, 2]
            cy: float = cam_matrix[1, 2]

            detections: list[pupil_apriltags.Detection] = self.detector.detect(
                gray,
                estimate_tag_pose=True,
                camera_params=(fx, fy, cx, cy),
                tag_size=self.tags[self.targetId],
            )

            tags_ids = []
            info: dict = None
            corners_all: list[tuple[int, list]] = []

            for detection in detections:

                tags_ids.append(detection.tag_id)
                corners_all.append((detection.tag_id, detection.corners.tolist()))

                if detection.tag_id == self.targetId:
                    pose_t: np.ndarray = detection.pose_t
                    pose_R: np.ndarray = detection.pose_R
                    distance: float = np.linalg.norm(pose_t)

                    center_x: float = detection.center[0]
                    center_y: float = detection.center[1]
                    angle_x: float = math.atan((center_x - cx) / fx)
                    angle_y: float = math.atan((center_y - cy) / fy)
                    corners: list[list[float]] = detection.corners.tolist()
                    yaw_error: float = np.degrees(
                        math.atan2(pose_R[1, 0], pose_R[0, 0])
                    )

                    info = {
                        "tag_id": detection.tag_id,
                        "angle_x": angle_x,
                        "angle_y": angle_y,
                        "distance": distance,
                        "corners": corners,
                        "pose_t": pose_t,
                        "pose_R": pose_R,
                        "yaw_error": yaw_error,
                    }

            best_id = self.get_best_id(tags_ids)
            if best_id is not None:
                self.targetId = best_id

            return info, corners_all
