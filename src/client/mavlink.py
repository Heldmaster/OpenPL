from pymavlink import mavutil
import logging
from typing import Optional

from src.internal.exception.exception import MavlinkConnectionError


class MavlinkClient:
    def __init__(self, connStr: str, logger: logging.Logger) -> None:
        self.connStr = connStr
        self.logger = logger
        self.master: Optional[mavutil.mavlink_connection] = None


    def connect(self) -> None:
        self.logger.info(f"Connecting to the drone: {self.connStr}...")
        try:
            self.master = mavutil.mavlink_connection(self.connStr, autoreconnect=True)
            self.master.wait_heartbeat()
            self.logger.info("Heartbeat received. Connection established.")
        except Exception as e:
            self.logger.critical(f"Failed to connect to drone: {e}")
            raise MavlinkConnectionError(f"Failed to connect to drone via {self.connStr}") from e


    def sendLandingTargetMessage(self, timeUs: int, targetNum: int, angleX: float, angleY: float, distance: float) -> None:
        if self.master is not None:
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
        else:
            self.logger.error("Error: Not connected to the drone.")
            return


    def landCommand(self) -> None:
        if self.master is not None:
            self.master.mav.command_long_send(
                self.master.target_system,
                self.master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_LAND,
                0, 0, 0, 0, 0, 0, 0, 0
            )
            self.logger.info("Sent land command to the drone.")
        else:
            self.logger.error("Error: Not connected to drone.")
            return
