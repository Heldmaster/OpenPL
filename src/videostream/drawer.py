import cv2
import numpy as np
from typing import Optional, Dict


class DebugDrawer:
    def __init__(self) -> None:
        pass

    def process_frame(
        self,
        frame: np.ndarray,
        cameraMatrix: np.ndarray,
        tagInfo: Optional[Dict[str, float]] = None,
        cornersAll: Optional[list[tuple[int, list]]] = None,
    ) -> np.ndarray:

        debug_frame = frame.copy()

        height, width = frame.shape[:2]
        info_text = f"Resolution: {width}x{height}"
        cv2.putText(debug_frame, info_text, (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

        if cornersAll:
            for tag in cornersAll:
                currentCorners = tag[1]
                intCorners = np.array(currentCorners, dtype=np.int32)
                cv2.polylines(
                    debug_frame,
                    [intCorners],
                    isClosed=True,
                    color=(0, 0, 255),
                    thickness=2,
                )

                centerX = int(np.mean(intCorners[:, 0]))
                centerY = int(np.mean(intCorners[:, 1]))

                cv2.putText(
                    debug_frame,
                    f"{tag[0]}",
                    (centerX, centerY),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                    cv2.LINE_AA,
                )

        if tagInfo:

            # Drawing outline on apriltags in frame
            if "corners" in tagInfo:
                corners = tagInfo["corners"]
                intCorners = np.array(corners, dtype=np.int32)
                cv2.polylines(
                    debug_frame,
                    [intCorners],
                    isClosed=True,
                    color=(0, 255, 0),
                    thickness=2,
                )

                centerX = int(np.mean(intCorners[:, 0]))
                centerY = int(np.mean(intCorners[:, 1]))

                cv2.putText(
                    debug_frame,
                    f"{tagInfo["tagId"]}",
                    (centerX, centerY),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )

            # Drawing axes on apriltag
            if "pose_R" in tagInfo and "pose_t" in tagInfo:
                R = tagInfo["pose_R"]
                t = tagInfo["pose_t"]

                cv2.drawFrameAxes(
                    debug_frame,
                    cameraMatrix,
                    np.zeros(
                        (4, 1), dtype=np.float32
                    ),  # TODO Add distortion coefficients
                    R,
                    t,
                    0.1,
                    thickness=2,
                )

        return debug_frame
