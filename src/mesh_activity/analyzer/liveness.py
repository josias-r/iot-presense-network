"""Liveness and health monitor for mesh sensors."""

from dataclasses import dataclass
import logging
import time
from typing import Dict, Optional
from mesh_activity.common.models import GeoPoint, SensorHeartbeat

logger = logging.getLogger(__name__)


@dataclass
class SensorState:
    sensor_id: str
    location: GeoPoint
    last_heartbeat_timestamp: float
    battery_pct: float
    is_online: bool = True


class LivenessMonitor:
    """Tracks known sensors, their locations, and health status."""

    def __init__(self, timeout_sec: float = 90.0) -> None:
        self.timeout_sec = timeout_sec
        self.sensors: Dict[str, SensorState] = {}

    def record_heartbeat(self, heartbeat: SensorHeartbeat) -> None:
        """Updates or registers a sensor from a received heartbeat."""
        now = time.time()
        if heartbeat.sensor_id not in self.sensors:
            logger.info(f"Registered new sensor [{heartbeat.sensor_id}] at ({heartbeat.location.latitude}, {heartbeat.location.longitude})")

        self.sensors[heartbeat.sensor_id] = SensorState(
            sensor_id=heartbeat.sensor_id,
            location=heartbeat.location,
            last_heartbeat_timestamp=now,
            battery_pct=heartbeat.battery_pct,
            is_online=True,
        )

    def set_node_status(self, sensor_id: str, is_online: bool) -> None:
        """Updates status directly from MQTT LWT events."""
        if sensor_id in self.sensors:
            self.sensors[sensor_id].is_online = is_online
            logger.warning(f"Sensor [{sensor_id}] status updated to: {'ONLINE' if is_online else 'OFFLINE'}")

    def check_dead_nodes(self) -> Dict[str, SensorState]:
        """Scans for sensors that have missed heartbeats beyond the timeout threshold."""
        now = time.time()
        dead = {}
        for s_id, state in self.sensors.items():
            if state.is_online and (now - state.last_heartbeat_timestamp > self.timeout_sec):
                state.is_online = False
                dead[s_id] = state
                logger.warning(f"Sensor [{s_id}] timed out! Marked as OFFLINE.")
        return dead

    def get_sensor_location(self, sensor_id: str) -> Optional[GeoPoint]:
        """Looks up the known coordinates of a sensor."""
        state = self.sensors.get(sensor_id)
        return state.location if state else None
