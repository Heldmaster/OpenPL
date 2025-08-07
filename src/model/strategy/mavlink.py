import time

from src.model.strategy.strategy import LandingStrategy
from src.cfg.config import REFRESH_RATE_SECONDS


class MavlinkLandingStrategy(LandingStrategy):
    def __init__(self, logger):
        super().__init__(logger)
        self.logger.info("Precision Landing Strategy initialized.")


    def land(self, drone, platform, mavlinkClient):
        self.logger.info("Executing precision landing strategy...")
        mavlinkClient.landCommand()

        while True:
            ret, frame = drone.camera.getFrame()
            if not ret:
                self.logger.warning("Could not get frame from camera.")
                continue

            tagInfo = platform.getInfo(frame)

            if tagInfo:
                self.logger.info(f"AprilTag with ID {tagInfo['tagId']} detected.")
                timeUs = int(time.time() * 1e6)
                mavlinkClient.sendLandingTargetMessage(
                    timeUs,
                    tagInfo['tagId'],
                    tagInfo['angleX'],
                    tagInfo['angleY'],
                    tagInfo['distance']
                )
            else:
                self.logger.info("No AprilTag detected.")

            time.sleep(REFRESH_RATE_SECONDS)
