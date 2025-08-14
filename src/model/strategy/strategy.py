import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.drone import Drone
    from src.model.platform import Platform
    from src.client.mavlink import MavlinkClient


class LandingStrategy(ABC):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    @abstractmethod
    def land(
        self,
        drone: "Drone",
        platform: "Platform",
        mavlinkClient: "MavlinkClient",
        refresh_rate: float,
        height_threshold: float,
    ) -> None:
        pass
