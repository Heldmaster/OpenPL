import numpy as np

from src.client.mavlink import MavlinkClient
from src.model.drone import Drone
from src.model.platform import AprilTagPlatform
from src.model.strategy.mavlink import MavlinkLandingStrategy
from src.internal.exception import CameraError, MavlinkConnectionError
from src.internal.logger.logger import setupLogger
from src.internal.config.parser import FileConfigParserFactory
from src.model.factory.camera import StreamCameraFactory
from src.videostreaming.streamer import VideoStreamerFactory

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

                camera = StreamCameraFactory.create(
                    config["camera"]["type"], logger, cameraMatrix, config
                )

                with camera as cam:
                    drone = Drone(
                        mavlinkClient=mavlinkClient,
                        camera=cam,
                        platform=platform,
                        landingStrategy=landingStrategy,
                        logger=logger,
                        config=config,
                    )

                    videostreamer = VideoStreamerFactory.create(
                        config["camera"]["streamer_type"], cam, platform
                    )
                    videostreamer.start()
                    drone.land()
                    videostreamer.stop()

    except CameraError as e:
        logger.critical(f"A camera-related error occurred: {e}")
    except MavlinkConnectionError as e:
        logger.critical(f"A drone connection error occurred: {e}")
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
    finally:
        logger.info("OpenPL Drone Landing Project Shutting Down")
