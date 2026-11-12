"""Trajectory extrapolation and road intersection prediction."""

from dataclasses import dataclass
import logging
from typing import Optional

from common.geo import project_point
from common.models import GeoPoint
from analyzer.tracker import EntityTrack

logger = logging.getLogger(__name__)


@dataclass
class TrajectoryPrediction:
    track_id: str
    projected_crossing: GeoPoint
    bearing_deg: float
    speed_mps: float
    time_to_crossing_sec: float
    confidence: float


class TrajectoryPredictor:
    """Estimates path forward and calculates projected intersection points."""

    def __init__(self, lookahead_sec: float = 60.0) -> None:
        self.lookahead_sec = lookahead_sec

    def predict(self, track: EntityTrack) -> Optional[TrajectoryPrediction]:
        """Calculates trajectory projection if track has sufficient observations."""
        # Require at least 2 points to establish speed and bearing
        if track.point_count < 2:
            return None

        speed = track.current_velocity_mps()
        bearing = track.current_bearing_deg()

        # In a full implementation: compute geometric intersection with road vectors.
        # Scaffolding logic: project forward along current bearing vector.
        projected_distance = speed * self.lookahead_sec
        latest_location = track.latest_point.location
        projected_point = project_point(latest_location, bearing, projected_distance)

        confidence = min(1.0, 0.5 + (track.point_count * 0.15))

        return TrajectoryPrediction(
            track_id=track.track_id,
            projected_crossing=projected_point,
            bearing_deg=bearing,
            speed_mps=speed,
            time_to_crossing_sec=self.lookahead_sec,
            confidence=confidence,
        )
