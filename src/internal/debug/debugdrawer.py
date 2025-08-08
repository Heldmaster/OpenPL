import cv2
import numpy as np
from typing import Optional, Dict

class DebugDrawer:
    def __init__(self, window_name: str = "DebugDraw") -> None:
        self._window_name = window_name
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)

    def draw(self, frame: np.ndarray, tagInfo: Optional[Dict[str, float]] = None) -> np.ndarray:
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

        return debug_frame
    
    def show_frame(self, frame: np.ndarray) -> None:
        cv2.imshow(self._window_name, frame)
        cv2.waitKey(1)

    def close(self) -> None:
        cv2.destroyWindow(self._window_name)