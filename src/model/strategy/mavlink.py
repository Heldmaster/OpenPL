import time
import numpy as np
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.drone import Drone
    from src.model.platform import Platform
    from src.client.mavlink import MavlinkClient

from src.model.strategy.strategy import LandingStrategy
from src.cfg.config import REFRESH_RATE_SECONDS, MAX_LANDING_TIME_SECONDS, HEIGHT_THRESHOLD_METERS


class MavlinkLandingStrategy(LandingStrategy):
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__(logger)
        self.logger.info("Precision Landing Strategy initialized.")

    def land(
        self, drone: "Drone", platform: "Platform", mavlinkClient: "MavlinkClient"
    ) -> None:
        self.logger.info("Executing precision landing strategy...")
        mavlinkClient.initiateLanding()
        time.sleep(REFRESH_RATE_SECONDS)

        start_time: float = time.time()
        while time.time() - start_time < MAX_LANDING_TIME_SECONDS:
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

                if tagInfo["distance"] < HEIGHT_THRESHOLD_METERS:
                    self.logger.info("Drone is close enough to land.")
                    break
            else:
                self.logger.info("No AprilTag detected.")

            time.sleep(REFRESH_RATE_SECONDS)

        if time.time() - start_time >= MAX_LANDING_TIME_SECONDS:
            self.logger.error("Landing timed out. Could not find or land on target.")
        else:
            self.logger.info("Landing strategy finished successfully.")
