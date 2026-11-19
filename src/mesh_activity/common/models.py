"""Domain data models and message schemas for the IoT Wildlife Mesh system."""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class GeoPoint:
    """Rep  resents a geographic point in WGS84 coordinate system."""
    latitude: float
    longitude: float
    elevation_m: Optional[float] = None


@dataclass
class SensorHeartbeat:
    """Sensor health and telemetry payload for alive infos"""
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
    """Event when sensors detect motion aka movement at their location"""
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
