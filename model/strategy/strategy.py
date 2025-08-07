from abc import ABC, abstractmethod


class LandingStrategy(ABC):
    def __init__(self, logger):
        self.logger = logger

    @abstractmethod
    def land(self, drone, platformDetector, mavlinkClient):
        pass
