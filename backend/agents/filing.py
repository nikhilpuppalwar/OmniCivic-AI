"""
OmniCivic AI -- Complaint Filing Agent
Creates formal complaint records. Filing is simulated and clearly labeled as such.
"""

from typing import Dict, Any
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))


async def file_complaint(
    incident: Dict[str, Any],
    perception_results: list,
    impact: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Complaint Filing Agent: Create a formal complaint record for an incident.
    Simulated filing, clearly labeled as such.
    """
    incident_id = incident.get("incident_id", "")
    connected = incident.get("connected_reports", [])
    priority = impact.get("priority", "MEDIUM")
    score = impact.get("score", 0)

    issue_types = list(set(p.get("issue_type", "") for p in perception_results))

    filing = {
        "filing_id": f"FILE-{incident_id}",
        "incident_id": incident_id,
        "filed_at": datetime.now(IST).isoformat(),
        "status": "FILED_SIMULATED",
        "disclaimer": "This is a simulated filing for demonstration purposes only.",
        "priority": priority,
        "impact_score": score,
        "issue_types": issue_types,
        "connected_reports": connected,
        "report_count": len(connected),
        "summary": (
            f"Civic incident {incident_id} involving {len(issue_types)} issue types "
            f"({', '.join(issue_types)}) across {len(connected)} citizen reports. "
            f"Priority: {priority} (Impact Score: {score}/100)."
        ),
    }

    agent_log = {
        "agent": "FILING_AGENT",
        "decision": f"Formal complaint filed as {filing['filing_id']} (SIMULATED)",
        "evidence_used": [
            f"Incident: {incident_id}",
            f"Reports: {len(connected)}",
            f"Priority: {priority}",
        ],
        "confidence": 1.0,
        "recommended_action": "Track resolution through SLA monitoring",
    }

    return {
        "filing": filing,
        "agent_log": agent_log,
    }
