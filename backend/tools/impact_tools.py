"""
OmniCivic AI -- Impact Tools
Weighted scoring formula for civic impact assessment.
"""

from typing import Dict, Any, List


# Weight distribution (must sum to 1.0)
WEIGHTS = {
    "severity": 0.30,
    "infrastructure_proximity": 0.20,
    "people_affected": 0.15,
    "duration": 0.10,
    "repeat_reports": 0.10,
    "secondary_risk": 0.15,
}

# Severity score mappings
SEVERITY_SCORES = {
    "CRITICAL": 100,
    "HIGH": 80,
    "MEDIUM": 50,
    "LOW": 25,
}

# Infrastructure proximity keywords and their scores (near schools, hospitals, etc.)
HIGH_PROXIMITY_KEYWORDS = [
    "school", "hospital", "temple", "church", "mosque", "station",
    "bus stop", "metro", "market", "playground", "college", "university",
]

# Issue types that carry secondary risk
SECONDARY_RISK_MAP = {
    "EXPOSED_WIRES": 95,     # Electrocution risk
    "SEWAGE_OVERFLOW": 80,   # Health hazard
    "WATERLOGGING": 65,      # Disease breeding, traffic accidents
    "WATER_LEAKAGE": 55,     # Structural damage risk
    "POTHOLE": 60,           # Vehicle accidents
    "ROAD_DAMAGE": 50,       # Vehicle damage
    "DRAIN_BLOCKAGE": 55,    # Flooding risk
    "DRAINAGE_PROBLEM": 50,  # Flooding risk
    "GARBAGE_OVERFLOW": 45,  # Health hazard
    "BROKEN_STREETLIGHT": 40, # Safety risk at night
}


def calculate_severity_score(perception_results: List[Dict]) -> float:
    """Calculate severity score from perception results (0-100)."""
    if not perception_results:
        return 0

    max_severity = "LOW"
    for p in perception_results:
        sev = p.get("severity", "LOW")
        if SEVERITY_SCORES.get(sev, 0) > SEVERITY_SCORES.get(max_severity, 0):
            max_severity = sev

    return SEVERITY_SCORES.get(max_severity, 25)


def calculate_infrastructure_proximity(reports: List[Dict]) -> float:
    """Calculate infrastructure proximity score based on nearby critical infrastructure (0-100)."""
    score = 30  # Base score

    for r in reports:
        desc = r.get("description", "").lower()
        addr = r.get("location", {}).get("address", "").lower()
        combined = desc + " " + addr

        for keyword in HIGH_PROXIMITY_KEYWORDS:
            if keyword in combined:
                score = max(score, 85)
                break

    return min(score, 100)


def calculate_people_affected(report_count: int, descriptions: List[str]) -> float:
    """Estimate people affected based on report count and description keywords (0-100)."""
    # Base: scale with report count
    base = min(report_count * 15, 60)

    # Boost for keywords indicating large impact
    impact_keywords = [
        "pedestrian", "commuter", "resident", "children", "elderly",
        "bus", "traffic", "market", "colony", "society", "building",
    ]

    keyword_boost = 0
    for desc in descriptions:
        desc_lower = desc.lower()
        for kw in impact_keywords:
            if kw in desc_lower:
                keyword_boost = max(keyword_boost, 30)
                break

    return min(base + keyword_boost, 100)


def calculate_duration_score(time_span_days: float) -> float:
    """Score based on how long the issue has persisted (0-100)."""
    if time_span_days <= 1:
        return 20
    elif time_span_days <= 3:
        return 50
    elif time_span_days <= 7:
        return 70
    elif time_span_days <= 14:
        return 85
    else:
        return 100


def calculate_repeat_reports_score(report_count: int) -> float:
    """Score based on number of repeat reports (0-100)."""
    if report_count <= 1:
        return 10
    elif report_count <= 2:
        return 30
    elif report_count <= 4:
        return 60
    elif report_count <= 6:
        return 80
    else:
        return 100


def calculate_secondary_risk(issue_types: List[str]) -> float:
    """Calculate secondary risk score based on issue types involved (0-100)."""
    if not issue_types:
        return 0

    max_risk = 0
    for it in issue_types:
        risk = SECONDARY_RISK_MAP.get(it, 25)
        if risk > max_risk:
            max_risk = risk

    # Boost for multiple different issue types (cascade risk)
    unique_types = len(set(issue_types))
    cascade_boost = min(unique_types * 5, 20)

    return min(max_risk + cascade_boost, 100)


def calculate_impact_score(
    perception_results: List[Dict],
    reports: List[Dict],
    time_span_days: float = 3.0,
) -> Dict[str, Any]:
    """
    Calculate the overall civic impact score (0-100) with breakdown.

    Weights:
    - Severity: 30%
    - Infrastructure proximity: 20%
    - People affected: 15%
    - Duration: 10%
    - Repeat reports: 10%
    - Secondary risk: 15%

    Returns dict with score, priority tier, and full breakdown.
    """
    descriptions = [r.get("description", "") for r in reports]
    issue_types = [p.get("issue_type", "") for p in perception_results]

    severity = calculate_severity_score(perception_results)
    proximity = calculate_infrastructure_proximity(reports)
    people = calculate_people_affected(len(reports), descriptions)
    duration = calculate_duration_score(time_span_days)
    repeats = calculate_repeat_reports_score(len(reports))
    secondary = calculate_secondary_risk(issue_types)

    # Weighted sum
    score = (
        severity * WEIGHTS["severity"] +
        proximity * WEIGHTS["infrastructure_proximity"] +
        people * WEIGHTS["people_affected"] +
        duration * WEIGHTS["duration"] +
        repeats * WEIGHTS["repeat_reports"] +
        secondary * WEIGHTS["secondary_risk"]
    )

    score = round(score, 1)

    # Priority tier (>=80 CRITICAL, 65-79 HIGH, 45-64 MEDIUM, <45 LOW)
    if score >= 80:
        priority = "CRITICAL"
    elif score >= 65:
        priority = "HIGH"
    elif score >= 45:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return {
        "score": score,
        "priority": priority,
        "breakdown": {
            "severity_score": round(severity, 1),
            "infrastructure_proximity": round(proximity, 1),
            "people_affected": round(people, 1),
            "duration": round(duration, 1),
            "repeat_reports": round(repeats, 1),
            "secondary_risk": round(secondary, 1),
        },
    }
