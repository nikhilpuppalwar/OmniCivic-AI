"""
OmniCivic AI -- Verification Tools
GPS matching, timestamp validation, and post-resolution complaint checking.
"""

from typing import List, Dict, Any, Optional
from tools.geo_tools import haversine
from tools.clustering_tools import parse_timestamp
from datetime import timedelta


def verify_location(
    before_lat: float,
    before_lon: float,
    after_lat: float,
    after_lon: float,
    threshold_m: float = 100.0,
) -> Dict[str, Any]:
    """
    Verify that the resolution evidence (after photo) GPS matches
    the incident location within threshold.
    """
    distance = haversine(before_lat, before_lon, after_lat, after_lon)

    return {
        "distance_m": round(distance, 1),
        "within_threshold": distance <= threshold_m,
        "threshold_m": threshold_m,
    }


def check_new_complaints(
    lat: float,
    lon: float,
    since_timestamp: str,
    complaints: List[Dict[str, Any]],
    radius_m: float = 200.0,
) -> List[Dict[str, Any]]:
    """
    Check for new complaints near the resolution location since the resolution was submitted.
    New complaints post-resolution may indicate the fix didn't work.
    """
    ref_dt = parse_timestamp(since_timestamp)
    new_complaints = []

    for c in complaints:
        c_dt = parse_timestamp(c.get("timestamp", ""))
        if c_dt <= ref_dt:
            continue  # Only look at complaints after resolution

        loc = c.get("location", {})
        c_lat = loc.get("latitude", 0)
        c_lon = loc.get("longitude", 0)

        dist = haversine(lat, lon, c_lat, c_lon)
        if dist <= radius_m:
            result = dict(c)
            result["_distance_m"] = round(dist, 1)
            new_complaints.append(result)

    return new_complaints


def verify_resolution_evidence(
    incident: Dict[str, Any],
    complaints: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Comprehensive resolution verification:
    1. GPS location match
    2. Check for new complaints post-resolution
    3. Image analysis (handled by the agent, not this tool)

    Returns verification result with confidence.
    """
    resolution = incident.get("resolution", {})
    after_photo = resolution.get("after_photo", "")
    after_gps = resolution.get("after_gps", {})

    # Get the incident cluster center as the reference point
    cluster = incident.get("cluster", {})
    ref_lat = cluster.get("center_lat", 0)
    ref_lon = cluster.get("center_lon", 0)

    # If no cluster center, use first connected report location
    if ref_lat == 0 and ref_lon == 0:
        connected = incident.get("connected_reports", [])
        for c in complaints:
            if c.get("report_id") in connected:
                loc = c.get("location", {})
                ref_lat = loc.get("latitude", 0)
                ref_lon = loc.get("longitude", 0)
                break

    after_lat = after_gps.get("latitude", 0)
    after_lon = after_gps.get("longitude", 0)

    # Step 1: Location verification
    location_check = verify_location(ref_lat, ref_lon, after_lat, after_lon)

    if not location_check["within_threshold"]:
        return {
            "verification_result": "LOCATION_MISMATCH",
            "verification_details": (
                f"Resolution evidence location is {location_check['distance_m']}m "
                f"from the incident site (threshold: {location_check['threshold_m']}m). "
                "The submitted photo does not appear to be from the correct location. "
                "Please submit evidence from the actual incident site. "
                "DO NOT CLOSE this incident."
            ),
            "confidence": 0.15,
            "location_check": location_check,
            "new_complaints": [],
        }

    # Step 2: Check for new complaints post-resolution
    submitted_at = resolution.get("submitted_at", "")
    new_complaints = []
    if submitted_at:
        new_complaints = check_new_complaints(
            ref_lat, ref_lon, submitted_at, complaints
        )

    if new_complaints:
        return {
            "verification_result": "POSSIBLE_FAILED_RESOLUTION",
            "verification_details": (
                f"Location verified (within {location_check['distance_m']}m), "
                f"but {len(new_complaints)} new complaint(s) have been filed "
                f"near this location since the resolution was submitted. "
                "This may indicate the issue has not been fully resolved. "
                "Physical inspection recommended before closing."
            ),
            "confidence": 0.45,
            "location_check": location_check,
            "new_complaints": [c.get("report_id") for c in new_complaints],
        }

    # Step 3: Passed all checks
    return {
        "verification_result": "RESOLUTION_VERIFIED",
        "verification_details": (
            f"Resolution evidence verified. Location match confirmed "
            f"(within {location_check['distance_m']}m of incident site). "
            "No new complaints detected post-resolution. "
            "Issue appears to be resolved."
        ),
        "confidence": 0.88,
        "location_check": location_check,
        "new_complaints": [],
    }
