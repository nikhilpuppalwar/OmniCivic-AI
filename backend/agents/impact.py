"""
OmniCivic AI -- Civic Impact Agent
Pure Python weighted scoring formula for impact assessment.
"""

from typing import Dict, Any, List
from datetime import datetime

from tools.impact_tools import calculate_impact_score
from tools.clustering_tools import parse_timestamp
from services.ai_service import generate_narrative


async def assess_impact(
    perception_results: List[Dict[str, Any]],
    cluster_reports: List[Dict[str, Any]],
    root_cause: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Civic Impact Agent: Calculate the weighted impact score and priority tier.

    Weights:
    - Severity: 30%
    - Infrastructure proximity: 20%
    - People affected: 15%
    - Duration: 10%
    - Repeat reports: 10%
    - Secondary risk: 15%

    Score: 0-100
    Tiers: LOW (0-25), MEDIUM (26-50), HIGH (51-75), CRITICAL (76-100)
    """
    # Calculate time span from earliest to latest report
    timestamps = [parse_timestamp(r.get("timestamp", "")) for r in cluster_reports]
    if timestamps:
        time_span = (max(timestamps) - min(timestamps)).total_seconds() / 86400
    else:
        time_span = 0

    # Run the scoring formula
    score_result = calculate_impact_score(
        perception_results=perception_results,
        reports=cluster_reports,
        time_span_days=time_span,
    )

    score = score_result["score"]
    priority = score_result["priority"]
    breakdown = score_result["breakdown"]

    # Generate explanation
    issue_types = list(set(p.get("issue_type", "") for p in perception_results))
    chain_str = " -> ".join(root_cause.get("chain", []))

    explanation = await generate_narrative(
        system_prompt=(
            "You are a civic impact analyst. Explain the impact score "
            "in 2-3 sentences, referencing specific breakdown factors."
        ),
        user_prompt=(
            f"Impact Score: {score}/100 ({priority})\n"
            f"Issue types: {', '.join(issue_types)}\n"
            f"Causal chain: {chain_str}\n"
            f"Reports: {len(cluster_reports)}\n"
            f"Duration: {time_span:.1f} days\n\n"
            f"Breakdown:\n"
            f"- Severity: {breakdown['severity_score']}/100 (weight: 30%)\n"
            f"- Infrastructure Proximity: {breakdown['infrastructure_proximity']}/100 (weight: 20%)\n"
            f"- People Affected: {breakdown['people_affected']}/100 (weight: 15%)\n"
            f"- Duration: {breakdown['duration']}/100 (weight: 10%)\n"
            f"- Repeat Reports: {breakdown['repeat_reports']}/100 (weight: 10%)\n"
            f"- Secondary Risk: {breakdown['secondary_risk']}/100 (weight: 15%)\n\n"
            "Explain the key factors driving this score."
        ),
        fallback_text=(
            f"Impact score of {score}/100 classified as {priority}. "
            f"Key factors: severity at {breakdown['severity_score']}/100, "
            f"infrastructure proximity at {breakdown['infrastructure_proximity']}/100, "
            f"and secondary risk at {breakdown['secondary_risk']}/100. "
            f"The cascading nature of {len(issue_types)} interconnected issue types "
            f"over {time_span:.1f} days significantly elevates the overall impact."
        ),
    )

    agent_log = {
        "agent": "IMPACT_AGENT",
        "decision": f"Impact Score: {score}/100 - {priority}",
        "evidence_used": [
            f"Severity: {breakdown['severity_score']}",
            f"Proximity: {breakdown['infrastructure_proximity']}",
            f"People affected: {breakdown['people_affected']}",
            f"Duration: {breakdown['duration']} ({time_span:.1f} days)",
            f"Repeat reports: {breakdown['repeat_reports']} ({len(cluster_reports)} reports)",
            f"Secondary risk: {breakdown['secondary_risk']}",
        ],
        "confidence": 0.90,
        "recommended_action": (
            "URGENT: Requires immediate multi-department response"
            if priority == "CRITICAL"
            else f"Schedule response per {priority} priority SLA"
        ),
    }

    return {
        "score": score,
        "priority": priority,
        "breakdown": breakdown,
        "explanation": explanation,
        "agent_log": agent_log,
    }
