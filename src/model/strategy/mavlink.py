import time
import numpy as np
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.drone import Drone
    from src.model.platform import Platform
    from src.client.mavlink import MavlinkClient

from src.model.strategy.strategy import LandingStrategy
from src.cfg.config import REFRESH_RATE_SECONDS


class MavlinkLandingStrategy(LandingStrategy):
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__(logger)
        self.logger.info("Precision Landing Strategy initialized.")

    def land(
        self, drone: "Drone", platform: "Platform", mavlinkClient: "MavlinkClient"
    ) -> None:
        self.logger.info("Executing precision landing strategy...")
        mavlinkClient.initiateLanding()

        while True:
            ret: bool
            frame: np.ndarray
            ret, frame = drone.camera.getFrame()
            if not ret:
                self.logger.warning("Could not get frame from camera.")
                continue

            tagInfo: dict[str, float] | None = platform.getInfo(frame)

            if tagInfo:
                self.logger.info(f"AprilTag with ID {tagInfo['tagId']} detected.")
                timeUs: int = int(time.time() * 1e6)
                mavlinkClient.updateLandingTarget(
                    timeUs,
                    int(tagInfo["tagId"]),
                    tagInfo["angleX"],
                    tagInfo["angleY"],
                    tagInfo["distance"],
                )
            else:
                self.logger.info("No AprilTag detected.")

            time.sleep(REFRESH_RATE_SECONDS)
