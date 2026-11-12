"""Domain data models and message schemas for the IoT Wildlife Mesh system."""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class GeoPoint:
    """Represents a geographic point in WGS84 coordinate system."""
    latitude: float
    longitude: float
    elevation_m: Optional[float] = None


@dataclass
class SensorHeartbeat:
    """Periodic health and telemetry payload emitted by sensor nodes."""
    sensor_id: str
    location: GeoPoint
    battery_pct: float
    timestamp: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SensorHeartbeat":
        location = GeoPoint(**data["location"])
        return cls(
            sensor_id=data["sensor_id"],
            location=location,
            battery_pct=data["battery_pct"],
            timestamp=data["timestamp"]
        )


@dataclass
class MotionEvent:
    """Event-driven movement trigger published by a sensor node."""
    event_id: str
    sensor_id: str
    location: GeoPoint
    timestamp: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    confidence: float = 1.0

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MotionEvent":
        location = GeoPoint(**data["location"])
        return cls(
            event_id=data["event_id"],
            sensor_id=data["sensor_id"],
            location=location,
            timestamp=data["timestamp"],
            confidence=data.get("confidence", 1.0)
        )


@dataclass
class SpatialHazardAlert:
    """Broadcast alert published by the Analyzer Node for autonomous sign activation."""
    alert_id: str
    track_id: str
    timestamp: float
    hazard_type: str
    projected_crossing: GeoPoint
    bearing_deg: float
    speed_mps: float
    time_to_crossing_sec: float
    confidence: float
    recommended_duration_sec: float = 30.0

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpatialHazardAlert":
        projected = GeoPoint(**data["projected_crossing"])
        return cls(
            alert_id=data["alert_id"],
            track_id=data["track_id"],
            timestamp=data["timestamp"],
            hazard_type=data["hazard_type"],
            projected_crossing=projected,
            bearing_deg=data["bearing_deg"],
            speed_mps=data["speed_mps"],
            time_to_crossing_sec=data["time_to_crossing_sec"],
            confidence=data["confidence"],
            recommended_duration_sec=data.get("recommended_duration_sec", 30.0)
        )
