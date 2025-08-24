import numpy as np
from src.client.mavlink import MavlinkClient
from src.internal.config.parser import FileConfigParserFactory
from src.internal.exception import CameraError, MavlinkConnectionError
from src.internal.logger.logger import setup_logger
from src.model.drone import Drone
from src.model.factory.camera import StreamCameraFactory
from src.model.platform import AprilTagPlatform
from src.model.strategy.mavlink import MavlinkLandingStrategy
from src.videostream.streamer import VideoStreamerFactory

if __name__ == "__main__":
    logger = setup_logger()
    logger.info("OpenPL Drone Landing Project Starting Up")

    config_parser = FileConfigParserFactory.create("toml", logger)
    config, tags = config_parser.parse("src/cfg/config.toml")

    try:
        camera_matrix: np.ndarray = np.array(
            [
                [config["camera_matrix"]["fx"], 0, config["camera_matrix"]["cx"]],
                [0, config["camera_matrix"]["fy"], config["camera_matrix"]["cy"]],
                [0, 0, 1],
            ]
        )

        mavlink_client = MavlinkClient(config["connection"]["string"], logger)
        platform = AprilTagPlatform(
            tags,
            logger,
        )
        landing_strategy = MavlinkLandingStrategy(logger, config)

        camera = StreamCameraFactory.create(
            config["camera"]["type"], logger, camera_matrix, config
        )

        videostreamer = VideoStreamerFactory.create(
            config["videostreaming"]["streamer_type"], camera, platform
        )

        if config["videostreaming"]["continuous"]:
            videostreamer.start()

        mavlink_client.connect()

        while True:
            if mavlink_client.is_landing:

                drone = Drone(
                    mavlink_client=mavlink_client,
                    camera=camera,
                    platform=platform,
                    landing_strategy=landing_strategy,
                    logger=logger,
                    config=config,
                )

                if not config["videostreaming"]["continuous"]:
                    videostreamer.start()

                drone.land()

                if not config["videostreaming"]["continuous"]:
                    videostreamer.stop()

    except CameraError as e:
        logger.critical(f"A camera-related error occurred: {e}")
    except MavlinkConnectionError as e:
        logger.critical(f"A drone connection error occurred: {e}")
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
    finally:
        logger.info("OpenPL Drone Landing Project Shutting Down")
