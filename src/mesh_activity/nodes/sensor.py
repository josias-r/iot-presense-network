"""Sensor Node: deploys in the forest, reports heartbeats and detects motion."""

import logging
import threading
import time
import uuid
from typing import Optional

from mesh_activity.common.config import Topics
from mesh_activity.common.models import GeoPoint, MotionEvent, SensorHeartbeat
from mesh_activity.common.mqtt_base import BaseMQTTNode

logger = logging.getLogger(__name__)


class SensorNode(BaseMQTTNode):
    """Represents a physical or simulated motion sensor in the forest mesh."""

    def __init__(
        self,
        sensor_id: str,
        location: GeoPoint,
        heartbeat_interval_sec: float = 30.0,
        battery_pct: float = 100.0,
    ) -> None:
        self.sensor_id = sensor_id
        self.location = location
        self.heartbeat_interval_sec = heartbeat_interval_sec
        self.battery_pct = battery_pct

        self._running = False
        self._heartbeat_thread: Optional[threading.Thread] = None

        super().__init__(
            client_id=f"sensor_{sensor_id}",
            lwt_topic=Topics.sensor_status(sensor_id),
            lwt_payload={"state": "offline", "sensor_id": sensor_id},
        )

    def on_connected(self) -> None:
        """Called once connected; starts the background heartbeat loop."""
        logger.info(f"SensorNode [{self.sensor_id}] initialized at ({self.location.latitude}, {self.location.longitude})")
        self._start_heartbeat_loop()

    def publish_heartbeat(self) -> None:
        """Publishes a heartbeat telemetry packet."""
        heartbeat = SensorHeartbeat(
            sensor_id=self.sensor_id,
            location=self.location,
            battery_pct=self.battery_pct,
        )
        topic = Topics.sensor_heartbeat(self.sensor_id)
        self.publish_json(topic, heartbeat.to_json(), qos=0)
        logger.debug(f"Heartbeat sent by [{self.sensor_id}]")

    def trigger_motion(self, confidence: float = 1.0) -> None:
        """Event triggered when movement is detected within the sensor range."""
        event = MotionEvent(
            event_id=str(uuid.uuid4())[:8],
            sensor_id=self.sensor_id,
            location=self.location,
            timestamp=time.time(),
            confidence=confidence,
        )
        topic = Topics.sensor_motion(self.sensor_id)
        self.publish_json(topic, event.to_json(), qos=1)
        logger.info(f"Motion DETECTED by [{self.sensor_id}] -> published to {topic}")

    def _start_heartbeat_loop(self) -> None:
        if self._running:
            return
        self._running = True

        def _loop() -> None:
            while self._running:
                self.publish_heartbeat()
                time.sleep(self.heartbeat_interval_sec)

        self._heartbeat_thread = threading.Thread(target=_loop, daemon=True)
        self._heartbeat_thread.start()

    def stop(self) -> None:
        """Stops the sensor node and disconnects cleanly."""
        self._running = False
        self.disconnect()


def main() -> None:
    """CLI entry point to run an individual sensor node."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Run a Mesh Sensor Node")
    parser.add_argument("--id", required=True, help="Unique sensor identifier (e.g. sensor_01)")
    parser.add_argument("--lat", type=float, required=True, help="Latitude coordinate (e.g. 47.3760)")
    parser.add_argument("--lon", type=float, required=True, help="Longitude coordinate (e.g. 8.5410)")
    parser.add_argument("--interval", type=float, default=15.0, help="Heartbeat interval in seconds")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    node = SensorNode(
        sensor_id=args.id,
        location=GeoPoint(latitude=args.lat, longitude=args.lon),
        heartbeat_interval_sec=args.interval,
    )
    node.connect()

    print(f"\n[Sensor {args.id}] Running at ({args.lat}, {args.lon}).")
    print(f"Press ENTER to trigger a motion detection event, or Ctrl+C to exit.\n")

    try:
        while True:
            # Wait for user input to simulate motion
            sys.stdin.readline()
            node.trigger_motion()
    except KeyboardInterrupt:
        print(f"\nShutting down sensor {args.id}...")
    finally:
        node.stop()


if __name__ == "__main__":
    main()

