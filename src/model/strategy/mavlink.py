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
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__(logger)
        self.logger.info("Precision Landing Strategy initialized.")
        self.debug_drawer: Optional[DebugDrawer] = None

    def land(
        self,
        drone: "Drone",
        platform: "Platform",
        mavlinkClient: "MavlinkClient",
        refresh_rate: float,
        height_threshold: float,
        debug_draw_enabled: bool,
    ) -> None:
        self.logger.info("Executing precision landing strategy...")

        if debug_draw_enabled:
            self.debug_drawer = DebugDrawer()

        while mavlinkClient.isLanding:

            if debug_draw_enabled and self.debug_drawer:
                _, frame = drone.camera.getFrame()
                debug_frame = self.debug_drawer.draw(frame, None)

            tagInfo: dict[str, float] | None = platform.getInfo(drone.camera)

            if tagInfo:
                self.logger.info(f"AprilTag with ID {tagInfo['tagId']} detected.")

                if debug_draw_enabled and self.debug_drawer:
                    ok, frame = drone.camera.getFrame()
                    if not ok:
                        self.logger.warning("Failed to get frame for debugging.")
                        continue
                    debug_frame = self.debug_drawer.draw(frame, tagInfo)

                timeUs: int = int(time.time() * 1e6)
                mavlinkClient.updateLandingTarget(
                    timeUs,
                    int(tagInfo["tagId"]),
                    tagInfo["angleX"],
                    tagInfo["angleY"],
                    tagInfo["distance"],
                )

                if tagInfo["distance"] < height_threshold:
                    self.logger.info("Drone is close enough to land.")
                    break
            else:
                self.logger.info("No AprilTag detected.")

            if debug_draw_enabled and self.debug_drawer:
                self.debug_drawer.show_frame(debug_frame)

            time.sleep(refresh_rate)

        if debug_draw_enabled and self.debug_drawer:
            self.debug_drawer.close()
