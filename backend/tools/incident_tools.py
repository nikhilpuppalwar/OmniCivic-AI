"""
OmniCivic AI -- Incident Tools
State machine helpers and ID generation for incident management.
"""

from typing import List, Dict, Any


# Valid status transitions
STATUS_TRANSITIONS = {
    "SUBMITTED": ["UNDER_REVIEW"],
    "UNDER_REVIEW": ["ASSIGNED", "SUBMITTED"],
    "ASSIGNED": ["ACTION_IN_PROGRESS", "UNDER_REVIEW"],
    "ACTION_IN_PROGRESS": ["AWAITING_RESOLUTION_EVIDENCE", "ESCALATED"],
    "AWAITING_RESOLUTION_EVIDENCE": ["RESOLUTION_REVIEW", "ESCALATED"],
    "RESOLUTION_REVIEW": ["RESOLVED", "REOPENED", "AWAITING_RESOLUTION_EVIDENCE"],
    "RESOLVED": ["REOPENED"],
    "REOPENED": ["UNDER_REVIEW", "ESCALATED"],
    "ESCALATED": ["UNDER_REVIEW", "ASSIGNED"],
}


def can_transition(current_status: str, new_status: str) -> bool:
    """Check if a status transition is valid."""
    valid_next = STATUS_TRANSITIONS.get(current_status, [])
    return new_status in valid_next


def classify_cluster(
    report_count: int,
    unique_issue_types: int,
    same_type_count: int,
) -> str:
    """
    Classify a cluster of reports:
    - 1 report, no matches -> INDEPENDENT_COMPLAINTS
    - Same type, close proximity -> DUPLICATE_REPORTS
    - 2-3 related types -> POSSIBLE_CONNECTED_INCIDENT
    - 4+ related types or high diversity -> HIGH_CONFIDENCE_CONNECTED_INCIDENT
    """
    if report_count <= 1:
        return "INDEPENDENT_COMPLAINTS"

    if unique_issue_types == 1 and same_type_count > 1:
        return "DUPLICATE_REPORTS"

    if unique_issue_types >= 4 or report_count >= 5:
        return "HIGH_CONFIDENCE_CONNECTED_INCIDENT"

    if unique_issue_types >= 2:
        return "POSSIBLE_CONNECTED_INCIDENT"

    return "DUPLICATE_REPORTS"


def get_unique_issue_types(perception_results: List[Dict]) -> List[str]:
    """Extract unique issue types from perception results."""
    return list(set(p.get("issue_type", "") for p in perception_results if p.get("issue_type")))
