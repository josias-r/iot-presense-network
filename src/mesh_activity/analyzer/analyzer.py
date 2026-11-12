"""Main Analyzer Node: orchestrates ingestion, tracking, trajectory prediction, and alert publishing."""

import logging
import time
import uuid
from typing import Any, Dict

from mesh_activity.common.config import Topics
from mesh_activity.common.models import MotionEvent, SensorHeartbeat, SpatialHazardAlert
from mesh_activity.common.mqtt_base import BaseMQTTNode
from mesh_activity.analyzer.liveness import LivenessMonitor
from mesh_activity.analyzer.tracker import SpatioTemporalCorrelator
from mesh_activity.analyzer.predictor import TrajectoryPredictor

logger = logging.getLogger(__name__)


class AnalyzerNode(BaseMQTTNode):
    """Central analytics processor monitoring forest mesh and broadcasting alerts."""

    def __init__(
        self,
        client_id: str = "analyzer_core_01",
        lookahead_sec: float = 30.0,
    ) -> None:
        super().__init__(client_id=client_id)

        self.liveness = LivenessMonitor()
        self.tracker = SpatioTemporalCorrelator()
        self.predictor = TrajectoryPredictor(lookahead_sec=lookahead_sec)

    def on_connected(self) -> None:
        """Subscribes to all sensor telemetry and status channels."""
        self.subscribe(Topics.SENSOR_HEARTBEAT_PATTERN, qos=0)
        self.subscribe(Topics.SENSOR_MOTION_PATTERN, qos=1)
        self.subscribe(Topics.SENSOR_STATUS_PATTERN, qos=1)
        logger.info(f"Analyzer Node [{self.client_id}] started and listening for forest telemetry.")

    def on_message_received(self, topic: str, payload: Dict[str, Any]) -> None:
        """Routes incoming messages to specialized pipeline stages."""
        if "/heartbeat" in topic:
            self._handle_heartbeat(payload)
        elif "/motion" in topic:
            self._handle_motion(payload)
        elif "/status" in topic:
            self._handle_status(payload)

    def _handle_heartbeat(self, payload: Dict[str, Any]) -> None:
        heartbeat = SensorHeartbeat.from_dict(payload)
        self.liveness.record_heartbeat(heartbeat)

    def _handle_status(self, payload: Dict[str, Any]) -> None:
        sensor_id = payload.get("sensor_id")
        is_online = payload.get("state") == "online"
        if sensor_id:
            self.liveness.set_node_status(sensor_id, is_online)

    def _handle_motion(self, payload: Dict[str, Any]) -> None:
        event = MotionEvent.from_dict(payload)
        track = self.tracker.ingest_motion_event(event)

        if track and track.point_count >= 2:
            prediction = self.predictor.predict(track)
            if prediction:
                self._dispatch_hazard_alert(prediction)

    def _dispatch_hazard_alert(self, pred: Any) -> None:
        """Publishes a decoupled spatial hazard alert to the MQTT broadcast channel."""
        alert = SpatialHazardAlert(
            alert_id=f"alt_{str(uuid.uuid4())[:8]}",
            track_id=pred.track_id,
            timestamp=time.time(),
            hazard_type="WILDLIFE_CROSSING",
            projected_crossing=pred.projected_crossing,
            bearing_deg=pred.bearing_deg,
            speed_mps=pred.speed_mps,
            time_to_crossing_sec=pred.time_to_crossing_sec,
            confidence=pred.confidence,
            recommended_duration_sec=30.0,
        )

        logger.warning(
            f"DISPATCHING ALERT [{alert.alert_id}] for Track [{alert.track_id}]: "
            f"crossing at ({alert.projected_crossing.latitude:.4f}, {alert.projected_crossing.longitude:.4f}) "
            f"in {alert.time_to_crossing_sec:.1f}s"
        )
        self.publish_json(Topics.ALERTS_GLOBAL, alert.to_json(), qos=1)


def main() -> None:
    """Entry point to run the standalone Analyzer node."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    analyzer = AnalyzerNode()
    analyzer.connect()
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopping Analyzer...")
    finally:
        analyzer.disconnect()


if __name__ == "__main__":
    main()

