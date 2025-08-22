import cv2
import numpy as np
from typing import Optional, Dict


class DebugDrawer:
    def __init__(self) -> None:
        pass

    def process_frame(
        self, frame: np.ndarray, cameraMatrix: np.ndarray, tagInfo: Optional[Dict[str, float]] = None,
    ) -> np.ndarray:
        debug_frame = frame.copy()

        if tagInfo:

            # Drawing outline on apriltags in frame
            if "corners" in tagInfo:
                corners = tagInfo["corners"]
                int_corners = np.array(corners, dtype=np.int32)
                cv2.polylines(
                    debug_frame,
                    [int_corners],
                    isClosed=True,
                    color=(0, 255, 0),
                    thickness=2,
                )

            # Drawing axes on apriltag
            if "pose_R" in tagInfo and "pose_t" in tagInfo:
                R = tagInfo["pose_R"]
                t = tagInfo["pose_t"]
                
                cv2.drawFrameAxes(
                    debug_frame,
                    cameraMatrix,
                    np.zeros((4, 1), dtype=np.float32), #TODO Add distortion coefficients
                    R,
                    t,
                    0.1,
                    thickness=2,
                )

        return debug_frame
