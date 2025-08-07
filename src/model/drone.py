class Drone:
    def __init__(self, mavlinkClient, camera, platform, landingStrategy, logger):
        self.mavlinkClient = mavlinkClient
        self.camera = camera
        self.platform = platform
        self.landingStrategy = landingStrategy
        self.logger = logger
        self.logger.info("Drone object initialized.")


    def land(self):
        self.mavlinkClient.connect()
        self.landingStrategy.land(self, self.platform, self.mavlinkClient)
