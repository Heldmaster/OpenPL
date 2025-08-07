from pymavlink import mavutil

from src.internal.exception.exception import MavlinkConnectionError


class MavlinkClient:
    def __init__(self, connStr, logger):
        self.connStr = connStr
        self.logger = logger
        self.master = None


    def connect(self):
        self.logger.info(f"Connecting to the drone: {self.connStr}...")
        try:
            self.master = mavutil.mavlink_connection(self.connStr, autoreconnect=True)
            self.master.wait_heartbeat()
            self.logger.info("Heartbeat received. Connection established.")
        except Exception as e:
            self.logger.critical(f"Failed to connect to drone: {e}")
            raise MavlinkConnectionError(f"Failed to connect to drone via {self.connStr}") from e


    def sendLandingTargetMessage(self, timeUs, targetNum, angleX, angleY, distance):
        if not self.master:
            self.logger.error("Error: Not connected to the drone.")
            return

        self.master.mav.landing_target_send(
            timeUs,
            targetNum,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            angleX,
            angleY,
            distance,
            0,
            0,
            0,
            0,
            0
        )
        self.logger.info(f"Sent LANDING_TARGET message for tag ID {targetNum} at {distance}.")


    def landCommand(self):
        if not self.master:
            self.logger.error("Error: Not connected to drone.")
            return

        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND,
            0, 0, 0, 0, 0, 0, 0, 0
        )

        self.logger.info("Sent land command to the drone.")
