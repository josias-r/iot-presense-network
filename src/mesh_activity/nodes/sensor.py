"""Sensor Node: deploys in the forest, reports heartbeats and detects motion."""

import logging

from mesh_activity.common.models import GeoPoint
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
        raise NotImplementedError

    def on_connected(self) -> None:
        """Called once connected; starts the background heartbeat loop."""
        raise NotImplementedError

    def publish_heartbeat(self) -> None:
        """Publishes a heartbeat telemetry packet."""
        raise NotImplementedError

    def trigger_motion(self, confidence: float = 1.0) -> None:
        """Event triggered when movement is detected within the sensor range."""
        raise NotImplementedError

    def _start_heartbeat_loop(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        """Stops the sensor node and disconnects cleanly."""
        raise NotImplementedError


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

