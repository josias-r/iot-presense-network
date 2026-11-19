"""Warning Sign Node: autonomous edge actuator filtering spatial alerts."""

import logging
import time
from typing import Any, Dict

from mesh_activity.common.models import GeoPoint
from mesh_activity.common.mqtt_base import BaseMQTTNode

logger = logging.getLogger(__name__)


class WarningSignNode(BaseMQTTNode):
    """An autonomous road sign that triggers warning signals if a hazard is nearby."""

    def __init__(
        self,
        sign_id: str,
        location: GeoPoint,
        warning_radius_meters: float = 250.0,
    ) -> None:
        raise NotImplementedError

    def on_connected(self) -> None:
        """Subscribes to global broadcast hazard alerts upon connection."""
        raise NotImplementedError

    def on_message_received(self, topic: str, payload: Dict[str, Any]) -> None:
        """Processes incoming broadcast alerts and performs edge geofence evaluation."""
        raise NotImplementedError

    def _evaluate_hazard(self, alert: Any) -> None:
        """Checks if the projected crossing coordinate is within this sign's safety radius."""
        raise NotImplementedError

    def activate_warning(self, duration_sec: float) -> None:
        """Engages physical/simulated warning indicators and starts a safety countdown."""
        raise NotImplementedError

    def deactivate_warning(self) -> None:
        """Turns off warning indicators."""
        raise NotImplementedError

    def stop(self) -> None:
        """Cleans up timers and disconnects."""
        raise NotImplementedError


def main() -> None:
    """CLI entry point to run an autonomous warning sign node."""
    import argparse

    parser = argparse.ArgumentParser(description="Run an Autonomous Warning Sign Node")
    parser.add_argument("--id", required=True, help="Unique sign identifier (e.g. sign_km12)")
    parser.add_argument("--lat", type=float, required=True, help="Latitude coordinate (e.g. 47.3780)")
    parser.add_argument("--lon", type=float, required=True, help="Longitude coordinate (e.g. 8.5430)")
    parser.add_argument("--radius", type=float, default=200.0, help="Warning activation radius in meters")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    sign = WarningSignNode(
        sign_id=args.id,
        location=GeoPoint(latitude=args.lat, longitude=args.lon),
        warning_radius_meters=args.radius,
    )
    sign.connect()

    print(f"\n[Warning Sign {args.id}] Active at ({args.lat}, {args.lon}) with radius {args.radius}m.")
    print("Listening for spatial hazard alerts (Press Ctrl+C to exit)...\n")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print(f"\nShutting down sign {args.id}...")
    finally:
        sign.stop()


if __name__ == "__main__":
    main()

