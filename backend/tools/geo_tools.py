"""
OmniCivic AI -- Geo Tools
Pure Python geographic computation: haversine distance, proximity search.
"""

import math
from typing import List, Dict, Any


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points in meters.
    Uses the Haversine formula.
    """
    R = 6_371_000  # Earth's radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_nearby_complaints(
    lat: float,
    lon: float,
    radius_m: float,
    complaints: List[Dict[str, Any]],
    exclude_id: str = "",
) -> List[Dict[str, Any]]:
    """
    Find all complaints within radius_m meters of (lat, lon).
    Returns list of complaints with distance added.
    """
    nearby = []
    for c in complaints:
        loc = c.get("location", {})
        c_lat = loc.get("latitude", 0)
        c_lon = loc.get("longitude", 0)

        if c_lat == 0 and c_lon == 0:
            continue

        dist = haversine(lat, lon, c_lat, c_lon)

        if dist <= radius_m and c.get("report_id") != exclude_id:
            result = dict(c)
            result["_distance_m"] = round(dist, 1)
            nearby.append(result)

    # Sort by distance
    nearby.sort(key=lambda x: x["_distance_m"])
    return nearby


def calculate_cluster_center(complaints: List[Dict[str, Any]]) -> tuple:
    """Calculate the geographic center (centroid) of a cluster of complaints."""
    if not complaints:
        return (0.0, 0.0)

    lats = []
    lons = []
    for c in complaints:
        loc = c.get("location", {})
        lats.append(loc.get("latitude", 0))
        lons.append(loc.get("longitude", 0))

    return (sum(lats) / len(lats), sum(lons) / len(lons))


def calculate_cluster_radius(
    complaints: List[Dict[str, Any]],
    center_lat: float,
    center_lon: float,
) -> float:
    """Calculate the maximum distance from center to any complaint in the cluster."""
    max_dist = 0
    for c in complaints:
        loc = c.get("location", {})
        dist = haversine(center_lat, center_lon,
                         loc.get("latitude", 0), loc.get("longitude", 0))
        if dist > max_dist:
            max_dist = dist
    return round(max_dist, 1)
