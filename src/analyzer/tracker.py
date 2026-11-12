"""Spatio-temporal correlation and multi-point entity tracking."""

from dataclasses import dataclass, field
import logging
import time
import uuid
from typing import List, Optional

from common.geo import calculate_bearing, haversine_distance
from common.models import GeoPoint, MotionEvent

logger = logging.getLogger(__name__)


@dataclass
class TrackObservation:
    event_id: str
    sensor_id: str
    location: GeoPoint
    timestamp: float


@dataclass
class EntityTrack:
    """Represents a moving entity observed across multiple sensor points."""
    track_id: str
    observations: List[TrackObservation] = field(default_factory=list)
    last_update_timestamp: float = field(default_factory=time.time)

    @property
    def latest_point(self) -> TrackObservation:
        return self.observations[-1]

    @property
    def point_count(self) -> int:
        return len(self.observations)

    def current_velocity_mps(self) -> float:
        """Calculates instantaneous speed between the last two observed points."""
        if len(self.observations) < 2:
            return 0.0
        p1 = self.observations[-2]
        p2 = self.observations[-1]
        dt = p2.timestamp - p1.timestamp
        if dt <= 0:
            return 0.0
        dist = haversine_distance(p1.location, p2.location)
        return dist / dt

    def current_bearing_deg(self) -> float:
        """Calculates compass heading between the last two observed points."""
        if len(self.observations) < 2:
            return 0.0
        return calculate_bearing(self.observations[-2].location, self.observations[-1].location)


class SpatioTemporalCorrelator:
    """Correlates isolated motion triggers into continuous entity tracks."""

    def __init__(
        self,
        max_distance_meters: float = 300.0,
        max_time_window_sec: float = 60.0,
        min_velocity_mps: float = 0.5,
        max_velocity_mps: float = 15.0,
    ) -> None:
        self.max_distance_meters = max_distance_meters
        self.max_time_window_sec = max_time_window_sec
        self.min_velocity_mps = min_velocity_mps
        self.max_velocity_mps = max_velocity_mps

        self.active_tracks: List[EntityTrack] = []

    def ingest_motion_event(self, event: MotionEvent) -> Optional[EntityTrack]:
        """Matches a motion event to an existing track or initializes a new candidate track."""
        obs = TrackObservation(
            event_id=event.event_id,
            sensor_id=event.sensor_id,
            location=event.location,
            timestamp=event.timestamp,
        )

        matched_track = self._find_matching_track(obs)
        if matched_track:
            matched_track.observations.append(obs)
            matched_track.last_update_timestamp = obs.timestamp
            logger.info(
                f"Correlated motion at {event.sensor_id} with Track [{matched_track.track_id}] "
                f"({matched_track.point_count} points, speed={matched_track.current_velocity_mps():.1f}m/s)"
            )
            return matched_track
        else:
            new_track = EntityTrack(
                track_id=f"trk_{str(uuid.uuid4())[:6]}",
                observations=[obs],
                last_update_timestamp=obs.timestamp,
            )
            self.active_tracks.append(new_track)
            logger.info(f"Initialized new candidate Track [{new_track.track_id}] at sensor [{event.sensor_id}]")
            return new_track

    def _find_matching_track(self, obs: TrackObservation) -> Optional[EntityTrack]:
        """Finds candidate track satisfying spatial and velocity gates."""
        for track in self.active_tracks:
            last_obs = track.latest_point
            dt = obs.timestamp - last_obs.timestamp

            if 0 < dt <= self.max_time_window_sec:
                dist = haversine_distance(last_obs.location, obs.location)
                if dist <= self.max_distance_meters:
                    velocity = dist / dt
                    if self.min_velocity_mps <= velocity <= self.max_velocity_mps:
                        return track
        return None

    def prune_stale_tracks(self, max_idle_sec: float = 120.0) -> None:
        """Removes tracks that have not received new observations."""
        now = time.time()
        self.active_tracks = [
            t for t in self.active_tracks if (now - t.last_update_timestamp) <= max_idle_sec
        ]
