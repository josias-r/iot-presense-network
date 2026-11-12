"""Geospatial calculations (distance, bearing, and projection)."""

import math
from mesh_activity.common.models import GeoPoint

EARTH_RADIUS_METERS = 6371000.0


def haversine_distance(p1: GeoPoint, p2: GeoPoint) -> float:
    """Calculates the great-circle distance between two geographic coordinates in meters."""
    lat1, lon1 = math.radians(p1.latitude), math.radians(p1.longitude)
    lat2, lon2 = math.radians(p2.latitude), math.radians(p2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_METERS * c


def calculate_bearing(p1: GeoPoint, p2: GeoPoint) -> float:
    """Calculates the initial forward bearing from p1 to p2 in degrees [0, 360)."""
    lat1, lon1 = math.radians(p1.latitude), math.radians(p1.longitude)
    lat2, lon2 = math.radians(p2.latitude), math.radians(p2.longitude)

    dlon = lon2 - lon1
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


def project_point(origin: GeoPoint, bearing_deg: float, distance_meters: float) -> GeoPoint:
    """Projects a point forward by a given distance (meters) along a compass bearing (degrees)."""
    lat1 = math.radians(origin.latitude)
    lon1 = math.radians(origin.longitude)
    bearing_rad = math.radians(bearing_deg)
    angular_distance = distance_meters / EARTH_RADIUS_METERS

    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance)
        + math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing_rad)
    )

    lon2 = lon1 + math.atan2(
        math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2)
    )

    return GeoPoint(latitude=math.degrees(lat2), longitude=math.degrees(lon2))
