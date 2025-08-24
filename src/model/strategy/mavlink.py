import logging
import time
from typing import TYPE_CHECKING, Optional

import numpy as np

if TYPE_CHECKING:
    from src.model.drone import Drone
    from src.model.platform import Platform
    from src.client.mavlink import MavlinkClient

from src.internal.debug.drawer import DebugDrawer
from src.model.strategy.strategy import LandingStrategy


class MavlinkLandingStrategy(LandingStrategy):
    def __init__(self, logger: logging.Logger, config: dict) -> None:
        super().__init__(logger, config)
        self.logger.info("Precision Landing Strategy initialized.")

    def land(
        self,
        drone: "Drone",
        platform: "Platform",
        mavlink_client: "MavlinkClient",
        refresh_rate: float,
        height_threshold: float,
    ) -> None:
        self.logger.info("Executing precision landing strategy...")

        while mavlink_client.is_landing:

            # tag_info: dict[str, float] | None = platform.get_info(drone.camera)
            result: tuple[Optional[dict[str, float]], list[tuple[int, list]]] | None = (
                platform.get_info(drone.camera)
            )
            tag_info, _ = result

            if tag_info:
                self.logger.info(f"AprilTag with ID {tag_info['tag_id']} detected.")

                time_us: int = int(time.time() * 1e6)
                mavlink_client.update_landing_target(
                    time_us,
                    int(tag_info["tag_id"]),
                    tag_info["angle_x"],
                    tag_info["angle_y"],
                    tag_info["distance"],
                )

                if self.config["yaw_correction"]["enabled"]:
                    mavlink_client.correct_yaw(
                        tag_info["yaw_error"],
                        self.config["yaw_correction"]["speed"],
                    )

                if tag_info["distance"] < height_threshold:
                    self.logger.info("Drone is close enough to land.")
                    break
            else:
                self.logger.info("No AprilTag detected.")

            time.sleep(refresh_rate)
