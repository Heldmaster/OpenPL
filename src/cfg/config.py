from typing import Dict

CONNECTION_STRING: str = "udp:127.0.0.1:14550"

CAMERA_INDEX: int = 0
CAMERA_MATRIX: Dict[str, float] = {
    "fx": 800.0,  # Focal length
    "fy": 800.0,
    "cx": 320.0,  # Optical center
    "cy": 240.0,
}


TARGET_TAG_ID: int = 1
TAG_SIZE_METERS: float = 0.16  # IRL size of the AprilTag (in meters)

REFRESH_RATE_SECONDS: float = 0.1
