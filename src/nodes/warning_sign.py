"""Warning Sign Node: autonomous edge actuator filtering spatial alerts."""

import logging
import threading
import time
from typing import Any, Dict, Optional

from common.config import Topics
from common.geo import haversine_distance
from common.models import GeoPoint, SpatialHazardAlert
from common.mqtt_base import BaseMQTTNode

logger = logging.getLogger(__name__)


class WarningSignNode(BaseMQTTNode):
    """An autonomous road sign that triggers warning signals if a hazard is nearby."""

    def __init__(
        self,
        sign_id: str,
        location: GeoPoint,
        warning_radius_meters: float = 250.0,
    ) -> None:
        self.sign_id = sign_id
        self.location = location
        self.warning_radius_meters = warning_radius_meters

        self.is_active = False
        self._countdown_timer: Optional[threading.Timer] = None

        super().__init__(
            client_id=f"warning_sign_{sign_id}",
            lwt_topic=Topics.warning_sign_status(sign_id),
            lwt_payload={"state": "offline", "sign_id": sign_id},
        )

    def on_connected(self) -> None:
        """Subscribes to global broadcast hazard alerts upon connection."""
        self.subscribe(Topics.ALERTS_GLOBAL, qos=1)
        logger.info(
            f"WarningSign [{self.sign_id}] active at ({self.location.latitude}, {self.location.longitude}) "
            f"with warning radius {self.warning_radius_meters}m"
        )

    def on_message_received(self, topic: str, payload: Dict[str, Any]) -> None:
        """Processes incoming broadcast alerts and performs edge geofence evaluation."""
        if topic == Topics.ALERTS_GLOBAL:
            alert = SpatialHazardAlert.from_dict(payload)
            self._evaluate_hazard(alert)

    def _evaluate_hazard(self, alert: SpatialHazardAlert) -> None:
        """Checks if the projected crossing coordinate is within this sign's safety radius."""
        dist = haversine_distance(self.location, alert.projected_crossing)

        if dist <= self.warning_radius_meters:
            logger.warning(
                f"[{self.sign_id}] ALERT TRIGGERED! Hazard distance={dist:.1f}m <= {self.warning_radius_meters}m. "
                f"Actuating lights for {alert.recommended_duration_sec}s"
            )
            self.activate_warning(duration_sec=alert.recommended_duration_sec)
        else:
            logger.debug(
                f"[{self.sign_id}] Hazard outside safety zone (dist={dist:.1f}m > {self.warning_radius_meters}m). Ignoring."
            )

    def activate_warning(self, duration_sec: float) -> None:
        """Engages physical/simulated warning indicators and starts a safety countdown."""
        self.is_active = True

        # Cancel any pending timeout to extend duration
        if self._countdown_timer and self._countdown_timer.is_alive():
            self._countdown_timer.cancel()

        self._countdown_timer = threading.Timer(duration_sec, self.deactivate_warning)
        self._countdown_timer.start()

    def deactivate_warning(self) -> None:
        """Turns off warning indicators."""
        self.is_active = False
        logger.info(f"[{self.sign_id}] Warning duration expired. Returning to IDLE.")

    def stop(self) -> None:
        """Cleans up timers and disconnects."""
        if self._countdown_timer:
            self._countdown_timer.cancel()
        self.disconnect()


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

