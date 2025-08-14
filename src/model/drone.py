import logging
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from src.client.mavlink import MavlinkClient
    from src.model.camera import Camera
    from src.model.platform import Platform
    from src.model.strategy.strategy import LandingStrategy


class Vehicle(ABC):
    @abstractmethod
    def land(self) -> None:
        pass


class Drone(Vehicle):
    def __init__(
        self,
        mavlinkClient: "MavlinkClient",
        camera: "Camera",
        platform: "Platform",
        landingStrategy: "LandingStrategy",
        logger: logging.Logger,
        config: dict,
    ) -> None:
        self.mavlinkClient = mavlinkClient
        self.camera = camera
        self.platform = platform
        self.landingStrategy = landingStrategy
        self.logger = logger
        self.config = config
        self.logger.info("Drone object initialized.")

    def land(self) -> None:
        self.landingStrategy.land(
            self,
            self.platform,
            self.mavlinkClient,
            self.config["landing"]["refresh_rate"],
            self.config["landing"]["height_threshold"],
            self.config["debug"]["drawer_enabled"],
        )
