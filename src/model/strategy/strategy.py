import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.client.mavlink import MavlinkClient
    from src.model.drone import Drone
    from src.model.platform import Platform


class LandingStrategy(ABC):
    def __init__(self, logger: logging.Logger, config: dict) -> None:
        self.logger = logger
        self.config = config

    @abstractmethod
    def land(
        self,
        drone: "Drone",
        platform: "Platform",
        mavlink_client: "MavlinkClient",
        refresh_rate: float,
        height_threshold: float,
    ) -> None:
        pass
