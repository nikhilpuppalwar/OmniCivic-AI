"""
OmniCivic AI -- Incident Detection Agent
Rule-based classification over clusters, LLM narrates the reasoning.
"""

from typing import Dict, Any, List

from tools.incident_tools import classify_cluster, get_unique_issue_types
from services.ai_service import generate_narrative


async def detect_incident(
    report: Dict[str, Any],
    perception_result: Dict[str, Any],
    cluster: Dict[str, Any],
    all_perception_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Incident Detection Agent: Classify whether a cluster of reports represents
    an independent complaint, duplicate, or connected incident.

    Classifications:
    - INDEPENDENT_COMPLAINTS: single report, no cluster
    - DUPLICATE_REPORTS: same issue type, close proximity
    - POSSIBLE_CONNECTED_INCIDENT: 2-3 related types
    - HIGH_CONFIDENCE_CONNECTED_INCIDENT: 4+ types or high diversity

    Returns classification with reasoning and agent log.
    """
    cluster_reports = cluster.get("reports", [])
    cluster_count = cluster.get("count", 0)
    report_id = report.get("report_id", "")

    # Count unique issue types across all perception results
    issue_types = get_unique_issue_types(all_perception_results)
    unique_type_count = len(issue_types)

    # Count same-type reports
    target_type = perception_result.get("issue_type", "")
    same_type_count = sum(
        1 for p in all_perception_results
        if p.get("issue_type") == target_type
    )

    # Rule-based classification
    classification = classify_cluster(
        report_count=cluster_count + 1,  # Include the target report
        unique_issue_types=unique_type_count,
        same_type_count=same_type_count,
    )

    # Generate LLM reasoning
    type_list = ", ".join(issue_types)
    reasoning = await generate_narrative(
        system_prompt=(
            "You are a civic incident analyst. Explain your incident detection "
            "classification in 2-3 sentences. Be precise about the evidence."
        ),
        user_prompt=(
            f"Report {report_id} triggered analysis.\n"
            f"Cluster size: {cluster_count + 1} reports\n"
            f"Issue types found: {type_list}\n"
            f"Same-type reports: {same_type_count}\n"
            f"Classification: {classification}\n\n"
            "Explain why this classification was chosen based on the evidence."
        ),
        fallback_text=(
            f"Based on {cluster_count + 1} reports with {unique_type_count} distinct issue types "
            f"({type_list}), classified as {classification}. "
            f"{'The diversity of issue types and spatial clustering strongly suggests a connected underlying incident.' if 'CONNECTED' in classification else 'Reports appear to be independent or duplicate filings.'}"
        ),
    )

    confidence = _calculate_detection_confidence(
        classification, cluster_count + 1, unique_type_count
    )

    agent_log = {
        "agent": "INCIDENT_DETECTION_AGENT",
        "decision": classification,
        "evidence_used": [
            f"Cluster size: {cluster_count + 1} reports",
            f"Unique issue types: {unique_type_count} ({type_list})",
            f"Same-type reports: {same_type_count}",
        ],
        "confidence": confidence,
        "recommended_action": (
            "Create incident and proceed to root cause analysis"
            if "CONNECTED" in classification
            else "File as independent complaint"
        ),
    }

    return {
        "classification": classification,
        "issue_types": issue_types,
        "reasoning": reasoning,
        "confidence": confidence,
        "agent_log": agent_log,
    }


def _calculate_detection_confidence(
    classification: str, report_count: int, type_count: int,
) -> float:
    """Calculate confidence score for the detection classification."""
    if classification == "HIGH_CONFIDENCE_CONNECTED_INCIDENT":
        return min(0.75 + report_count * 0.02 + type_count * 0.03, 0.95)
    elif classification == "POSSIBLE_CONNECTED_INCIDENT":
        return min(0.55 + report_count * 0.03, 0.80)
    elif classification == "DUPLICATE_REPORTS":
        return min(0.70 + report_count * 0.05, 0.92)
    else:
        return 0.50
