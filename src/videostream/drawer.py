from typing import Dict, Optional

import cv2
import numpy as np


class DebugDrawer:
    def __init__(self) -> None:
        pass

    def process_frame(
        self,
        frame: np.ndarray,
        camera_matrix: np.ndarray,
        tag_info: Optional[Dict[str, float]] = None,
        corners_all: Optional[list[tuple[int, list]]] = None,
    ) -> np.ndarray:

        debug_frame = frame.copy()

        if corners_all:
            for tag in corners_all:
                curr_corners = tag[1]
                int_corners = np.array(curr_corners, dtype=np.int32)
                cv2.polylines(
                    debug_frame,
                    [int_corners],
                    isClosed=True,
                    color=(0, 0, 255),
                    thickness=2,
                )

                center_x = int(np.mean(int_corners[:, 0]))
                center_y = int(np.mean(int_corners[:, 1]))

                cv2.putText(
                    debug_frame,
                    f"{tag[0]}",
                    (center_x, center_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                    cv2.LINE_AA,
                )

        if tag_info:

            # Drawing outline on apriltags in frame
            if "corners" in tag_info:
                corners = tag_info["corners"]
                int_corners = np.array(corners, dtype=np.int32)
                cv2.polylines(
                    debug_frame,
                    [int_corners],
                    isClosed=True,
                    color=(0, 255, 0),
                    thickness=2,
                )

                center_x = int(np.mean(int_corners[:, 0]))
                center_y = int(np.mean(int_corners[:, 1]))

                cv2.putText(
                    debug_frame,
                    f"{tag_info["tag_id"]}",
                    (center_x, center_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )

            # Drawing axes on apriltag
            if "pose_R" in tag_info and "pose_t" in tag_info:
                R = tag_info["pose_R"]
                t = tag_info["pose_t"]

                cv2.drawFrameAxes(
                    debug_frame,
                    camera_matrix,
                    np.zeros(
                        (4, 1), dtype=np.float32
                    ),  # TODO Add distortion coefficients
                    R,
                    t,
                    0.1,
                    thickness=2,
                )

        return debug_frame
