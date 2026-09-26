"""
OmniCivic AI -- Clustering Tools
Time-window filtering and complaint clustering logic.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

from tools.geo_tools import haversine, get_nearby_complaints, calculate_cluster_center, calculate_cluster_radius


def parse_timestamp(ts: str) -> datetime:
    """Parse an ISO timestamp string to datetime."""
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return datetime.now()


def get_recent_complaints(
    reference_timestamp: str,
    window_days: int,
    complaints: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Filter complaints that fall within window_days before the reference timestamp.
    """
    ref_dt = parse_timestamp(reference_timestamp)
    cutoff = ref_dt - timedelta(days=window_days)

    recent = []
    for c in complaints:
        c_dt = parse_timestamp(c.get("timestamp", ""))
        if cutoff <= c_dt <= ref_dt:
            recent.append(c)

    return recent


def cluster_complaints(
    target_report: Dict[str, Any],
    all_complaints: List[Dict[str, Any]],
    radius_m: float = 180.0,
    window_days: int = 7,
) -> Dict[str, Any]:
    """
    Cluster complaints that are near the target report in both space and time.

    Returns a cluster dict with:
    - reports: list of clustered complaint dicts
    - center: (lat, lon) tuple
    - radius_m: actual cluster radius
    - time_window_days: window used
    - count: number of reports in cluster
    """
    loc = target_report.get("location", {})
    target_lat = loc.get("latitude", 0)
    target_lon = loc.get("longitude", 0)
    target_id = target_report.get("report_id", "")
    target_ts = target_report.get("timestamp", "")

    # Step 1: Filter by time window (reports within window_days of target)
    ref_dt = parse_timestamp(target_ts)
    time_start = ref_dt - timedelta(days=window_days)
    time_end = ref_dt + timedelta(days=window_days)

    time_filtered = []
    for c in all_complaints:
        c_dt = parse_timestamp(c.get("timestamp", ""))
        if time_start <= c_dt <= time_end and c.get("report_id") != target_id:
            time_filtered.append(c)

    # Step 2: Filter by distance
    nearby = get_nearby_complaints(
        target_lat, target_lon, radius_m,
        time_filtered, exclude_id=target_id,
    )

    # Step 3: Calculate cluster metrics
    all_in_cluster = [target_report] + nearby
    center_lat, center_lon = calculate_cluster_center(all_in_cluster)
    actual_radius = calculate_cluster_radius(all_in_cluster, center_lat, center_lon)

    return {
        "reports": nearby,
        "center_lat": center_lat,
        "center_lon": center_lon,
        "radius_m": actual_radius,
        "time_window_days": window_days,
        "count": len(nearby),
        "report_ids": [r.get("report_id") for r in nearby],
    }
