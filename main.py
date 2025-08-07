import numpy as np

from cfg.config import CAMERA_MATRIX, CAMERA_INDEX, CONNECTION_STRING, TARGET_TAG_ID, TAG_SIZE_METERS
from client.mavlink import MavlinkClient
from model.drone import Drone
from model.platform import Platform
from model.camera import Camera
from model.strategy.mavlink import MavlinkLandingStrategy
from internal.exception import CameraError, MavlinkConnectionError
from internal.logger.logger import setupLogger

if __name__ == '__main__':
    logger = setupLogger()
    logger.info("OpenPL Drone Landing Project Starting Up")

    try:
        cameraMatrix = np.array([
            [CAMERA_MATRIX['fx'], 0, CAMERA_MATRIX['cx']],
            [0, CAMERA_MATRIX['fy'], CAMERA_MATRIX['cy']],
            [0, 0, 1]
        ])

        mavlinkClient = MavlinkClient(CONNECTION_STRING, logger)
        platform = Platform(TARGET_TAG_ID, TAG_SIZE_METERS, cameraMatrix, logger)
        landingStrategy = MavlinkLandingStrategy(logger)

        with Camera(CAMERA_INDEX, logger) as camera:
            drone = Drone(
                mavlinkClient=mavlinkClient,
                camera=camera,
                platform=platform,
                landingStrategy=landingStrategy,
                logger=logger
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
