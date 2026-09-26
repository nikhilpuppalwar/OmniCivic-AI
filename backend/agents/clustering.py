"""
OmniCivic AI -- Geo-Temporal Clustering Agent
Finds spatially and temporally related complaints using pure Python distance/time math.
"""

import json
import os
from typing import Dict, Any, List

from tools.clustering_tools import cluster_complaints
from services.ai_service import generate_narrative

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _load_complaints() -> List[Dict]:
    path = os.path.join(DATA_DIR, "complaints.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("reports", [])


async def find_cluster(
    report: Dict[str, Any],
    radius_m: float = 180.0,
    window_days: int = 7,
) -> Dict[str, Any]:
    """
    Geo-Temporal Clustering Agent: Find nearby and recent complaints
    related to the target report.

    Uses haversine distance and time-window filtering.

    Returns cluster info with related report IDs and agent log.
    """
    all_complaints = _load_complaints()

    cluster = cluster_complaints(
        target_report=report,
        all_complaints=all_complaints,
        radius_m=radius_m,
        window_days=window_days,
    )

    report_id = report.get("report_id", "")
    cluster_count = cluster["count"]

    # Generate LLM reasoning about the cluster
    if cluster_count > 0:
        report_summaries = []
        for r in cluster["reports"][:8]:  # Limit to 8 for prompt size
            report_summaries.append(
                f"- {r.get('report_id')}: {r.get('description', '')[:100]}... "
                f"(distance: {r.get('_distance_m', 0)}m)"
            )
        summaries_text = "\n".join(report_summaries)

        reasoning = await generate_narrative(
            system_prompt=(
                "You are a civic data analyst. Explain why these complaints "
                "may be related based on their proximity and timing."
            ),
            user_prompt=(
                f"Target report {report_id}: {report.get('description', '')[:150]}\n\n"
                f"Found {cluster_count} nearby reports within {radius_m}m "
                f"and {window_days} days:\n{summaries_text}\n\n"
                "Briefly explain the spatial and temporal relationship between these reports."
            ),
            fallback_text=(
                f"Found {cluster_count} related reports within {radius_m}m radius "
                f"and {window_days}-day window. The geographic clustering and temporal "
                f"proximity suggest these complaints may share a common underlying cause."
            ),
        )
    else:
        reasoning = "No related reports found within the search parameters. This appears to be an isolated complaint."

    agent_log = {
        "agent": "CLUSTERING_AGENT",
        "decision": f"Found {cluster_count} related reports in cluster",
        "evidence_used": [
            f"Search radius: {radius_m}m",
            f"Time window: {window_days} days",
            f"Center: ({cluster['center_lat']:.4f}, {cluster['center_lon']:.4f})",
            f"Cluster radius: {cluster['radius_m']}m",
        ],
        "confidence": min(0.5 + cluster_count * 0.1, 0.95),
        "recommended_action": (
            "Proceed to incident detection" if cluster_count > 0
            else "File as independent complaint"
        ),
    }

    return {
        "cluster": cluster,
        "reasoning": reasoning,
        "agent_log": agent_log,
    }
