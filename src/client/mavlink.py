from pymavlink import mavutil
import logging
from typing import Optional

from src.internal.exception.exception import MavlinkConnectionError


class MavlinkClient:
    def __init__(self, connStr: str, logger: logging.Logger) -> None:
        self.connStr = connStr
        self.logger = logger
        self.master: Optional[mavutil.mavlink_connection] = None

        self._last_mode: Optional[str] = None
        self._last_mission_command: Optional[int] = None
        self._armed: Optional[bool] = None

    def connect(self) -> None:
        self.logger.info(f"Connecting to the drone: {self.connStr}...")
        try:
            self.master = mavutil.mavlink_connection(self.connStr, autoreconnect=True)
            self.master.wait_heartbeat()
            self.logger.info("Heartbeat received. Connection established.")
        except Exception as e:
            self.logger.critical(f"Failed to connect to drone: {e}")
            raise MavlinkConnectionError(
                f"Failed to connect to drone via {self.connStr}"
            ) from e

    @property
    def isLanding(self) -> bool:
        """
        Returns True if vehicle is landing somehow (in LAND mode or performing landing due to mission point) and armed
        """
        msg = self.master.recv_match(type="HEARTBEAT", blocking=False)
        if msg:
            self._last_mode = mavutil.mode_string_v10(msg)
            self._armed = (
                msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
            ) != 0

        mission_msg = self.master.recv_match(type="MISSION_CURRENT", blocking=False)
        if mission_msg:
            seq = mission_msg.seq

            self.master.mav.mission_request_int_send(
                self.master.target_system,
                self.master.target_component,
                seq,
            )

            item_msg = self.master.recv_match(
                type="MISSION_ITEM_INT", blocking=True, timeout=0.01
            )  # blocking because otherwise we'll miss requested message
            if item_msg:
                self._last_mission_command = item_msg.command

        # TODO return True only if precland is enabled in MAV_CMD_NAV_LAND, idk how to check param2 properly :(
        if self._armed and (
            self._last_mode == "LAND" or self._last_mission_command == 21
        ):
            return True
        else:
            return False

    def updateLandingTarget(
        self, timeUs: int, targetNum: int, angleX: float, angleY: float, distance: float
    ) -> None:
        if self.master is not None:
            self.master.mav.landing_target_send(
                timeUs,
                targetNum,
                mavutil.mavlink.MAV_FRAME_BODY_FRD,
                -1*angleX,
                -1*angleY,
                distance,
                0,
                0,
                0,
                0,
            )
            self.logger.info(
                f"Sent LANDING_TARGET message for tag ID {targetNum} at {distance}."
            )
        else:
            self.logger.error("Error: Not connected to the drone.")
            return
