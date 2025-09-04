import numpy as np

from src.client.mavlink import MavlinkClient
from src.model.drone import Drone
from src.model.platform import AprilTagPlatform
from src.model.strategy.mavlink import MavlinkLandingStrategy
from src.internal.exception import CameraError, MavlinkConnectionError
from src.internal.logger.logger import setupLogger
from src.internal.config.parser import FileConfigParserFactory
from src.model.factory.camera import StreamCameraFactory
from src.videostream.streamer import VideoStreamerFactory

if __name__ == "__main__":
    logger = setupLogger()
    logger.info("OpenPL Drone Landing Project Starting Up")

    config_parser = FileConfigParserFactory.create("toml", logger)
    config, tags = config_parser.parse("src/cfg/config.toml")

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
            tags,
            logger,
        )
        landingStrategy = MavlinkLandingStrategy(logger, config)

        camera = StreamCameraFactory.create(
            config["camera"]["type"], logger, cameraMatrix, config
        )

        if config["videostreaming"]["always_detect"]:
            videostreamer = VideoStreamerFactory.create(
                config["videostreaming"]["streamer_type"], camera, platform
            )
        else:
            videostreamer = VideoStreamerFactory.create(
                config["videostreaming"]["streamer_type"], camera, None
            )

        if config["videostreaming"]["continuous"]:
            videostreamer.start()

        mavlinkClient.connect()

        while True:
            if mavlinkClient.isLanding:

                drone = Drone(
                    mavlinkClient=mavlinkClient,
                    camera=camera,
                    platform=platform,
                    landingStrategy=landingStrategy,
                    logger=logger,
                    config=config,
                )

                if not config["videostreaming"]["continuous"]:
                    videostreamer.platform = platform
                    videostreamer.start()

                drone.land()

                if not config["videostreaming"]["continuous"]:
                    videostreamer.stop()
                    videostreamer.platform = None

    except CameraError as e:
        logger.critical(f"A camera-related error occurred: {e}")
    except MavlinkConnectionError as e:
        logger.critical(f"A drone connection error occurred: {e}")
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
    finally:
        logger.info("OpenPL Drone Landing Project Shutting Down")
