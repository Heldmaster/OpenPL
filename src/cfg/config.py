from typing import Dict

# Mavlink connection settings
CONNECTION_STRING: str = "udp:127.0.0.1:14550"

# Camera settings
CAMERA_INDEX: int = 0
CAMERA_MATRIX: Dict[str, float] = {
    "fx": 800.0,  # Focal length
    "fy": 800.0,
    "cx": 320.0,  # Optical center
    "cy": 240.0,
}


# AprilTag settings
TARGET_TAG_ID: int = 1
TAG_SIZE_METERS: float = 0.16  # IRL size of the AprilTag (in meters)


# Landing parameters
REFRESH_RATE_SECONDS: float = 0.1
MAX_LANDING_TIME_SECONDS: float = 60.0
HEIGHT_THRESHOLD_METERS: float = 0.1


# Simualtion mode settings
SIMULATION_MODE: bool = True