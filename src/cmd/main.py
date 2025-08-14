import numpy as np

from src.client.mavlink import MavlinkClient
from src.model.drone import Drone
from src.model.platform import AprilTagPlatform
from src.model.camera import DefaultCamera
from src.model.strategy.mavlink import MavlinkLandingStrategy
from src.internal.exception import CameraError, MavlinkConnectionError
from src.internal.logger.logger import setupLogger
from src.internal.config.parser import FileConfigParserFactory

if __name__ == "__main__":
    logger = setupLogger()
    logger.info("OpenPL Drone Landing Project Starting Up")

    config_parser = FileConfigParserFactory.create("toml", logger)
    config = config_parser.parse("src/cfg/config.toml")

    try:
        cameraMatrix: np.ndarray = np.array(
            [
                [config["camera_matrix"]["fx"], 0, config["camera_matrix"]["cx"]],
                [0, config["camera_matrix"]["fy"], config["camera_matrix"]["cy"]],
                [0, 0, 1],
            ]
        )

        mavlinkClient = MavlinkClient(config["connection"]["string"], logger)
        platform = AprilTagPlatform(
            config["apriltag"]["target_tag_id"], config["apriltag"]["tag_size"], logger
        )
        landingStrategy = MavlinkLandingStrategy(logger)

        mavlinkClient.connect()

        while True:
            if mavlinkClient.isLanding:

                with DefaultCamera(
                    config["camera"]["index"], cameraMatrix, logger
                ) as defaultCamera:
                    drone = Drone(
                        mavlinkClient=mavlinkClient,
                        camera=defaultCamera,
                        platform=platform,
                        landingStrategy=landingStrategy,
                        logger=logger,
                    )

                    drone.land()

    except CameraError as e:
        logger.critical(f"A camera-related error occurred: {e}")
    except MavlinkConnectionError as e:
        logger.critical(f"A drone connection error occurred: {e}")
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
    finally:
        logger.info("OpenPL Drone Landing Project Shutting Down")
