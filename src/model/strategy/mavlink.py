import time
import numpy as np
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.model.drone import Drone
    from src.model.platform import Platform
    from src.client.mavlink import MavlinkClient

from src.model.strategy.strategy import LandingStrategy
from src.internal.debug.drawer import DebugDrawer


class MavlinkLandingStrategy(LandingStrategy):
    def __init__(self, logger: logging.Logger, config: dict) -> None:
        super().__init__(logger, config)
        self.logger.info("Precision Landing Strategy initialized.")

    def land(
        self,
        drone: "Drone",
        platform: "Platform",
        mavlinkClient: "MavlinkClient",
        refresh_rate: float,
        height_threshold: float,
    ) -> None:
        self.logger.info("Executing precision landing strategy...")

        while mavlinkClient.isLanding:

            # tagInfo: dict[str, float] | None = platform.getInfo(drone.camera)
            result: tuple[Optional[dict[str, float]], list[tuple[int, list]]] | None = (
                platform.getInfo(drone.camera)
            )
            tagInfo, _ = result

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

                if self.config["yaw_correction"]["enabled"]:
                    mavlinkClient.correctYaw(
                        tagInfo["yawError"],
                        self.config["yaw_correction"]["speed"],
                    )

                if tagInfo["distance"] < height_threshold:
                    self.logger.info("Drone is close enough to land.")
                    break
            else:
                self.logger.info("No AprilTag detected.")

            time.sleep(refresh_rate)
