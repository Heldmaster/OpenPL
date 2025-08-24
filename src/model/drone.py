import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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
        mavlink_client: "MavlinkClient",
        camera: "Camera",
        platform: "Platform",
        landing_strategy: "LandingStrategy",
        logger: logging.Logger,
        config: dict,
    ) -> None:
        self.mavlink_client = mavlink_client
        self.camera = camera
        self.platform = platform
        self.landing_strategy = landing_strategy
        self.logger = logger
        self.config = config
        self.logger.info("Drone object initialized.")

    def land(self) -> None:
        self.landing_strategy.land(
            self,
            self.platform,
            self.mavlink_client,
            self.config["landing"]["refresh_rate_seconds"],
            self.config["landing"]["height_threshold"],
        )
