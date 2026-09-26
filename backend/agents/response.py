"""
OmniCivic AI -- Response Orchestration Agent
Department knowledge-base lookup, dependency-ordered multi-department response plan.
LLM explains the ordering rationale.
"""

from typing import Dict, Any, List

from tools.knowledge_tools import get_response_order
from services.ai_service import generate_narrative


async def create_response_plan(
    issue_types: List[str],
    impact_score: Dict[str, Any],
    root_cause: Dict[str, Any],
    cluster_reports: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Response Orchestration Agent: Create a dependency-ordered multi-department
    response plan based on the identified issues.

    The plan requires human approval before execution (human-in-the-loop gate).
    """
    # Get ordered department response steps
    response_steps = get_response_order(issue_types)

    # Calculate estimated hours based on priority
    priority = impact_score.get("priority", "MEDIUM")

    steps = []
    for step in response_steps:
        sla = step.get("sla_hours", {})
        estimated = sla.get(priority, 48)

        steps.append({
            "step_number": step["step_number"],
            "department": step["department"],
            "department_name": step["department_name"],
            "action": step["action"],
            "reason": step["reason"],
            "estimated_hours": estimated,
            "depends_on": [s["department"] for s in response_steps
                           if s["department"] in step.get("depends_on", [])],
            "resources": step.get("resources", []),
            "issues": step.get("issues", []),
        })

    # Generate rationale
    chain_str = " -> ".join(root_cause.get("chain", []))
    steps_summary = "\n".join(
        f"Step {s['step_number']}: {s['department_name']} - {s['action']} "
        f"(est. {s['estimated_hours']}h)"
        for s in steps
    )

    rationale = await generate_narrative(
        system_prompt=(
            "You are a civic response planner. Explain the department response "
            "ordering in 3-4 sentences. Focus on why this order matters."
        ),
        user_prompt=(
            f"Root cause chain: {chain_str}\n"
            f"Priority: {priority} (score: {impact_score.get('score', 0)})\n\n"
            f"Response plan:\n{steps_summary}\n\n"
            "Explain why the departments are ordered this way. "
            "Focus on dependencies — which fixes must come first and why."
        ),
        fallback_text=(
            f"The response plan follows a dependency-ordered sequence to ensure "
            f"root cause fixes precede downstream repairs. "
            f"{'Emergency services prioritized due to CRITICAL severity. ' if priority == 'CRITICAL' else ''}"
            f"Road repairs are deliberately scheduled after water/drainage fixes "
            f"because repairing road surfaces over an active water leak would waste resources "
            f"and require re-work."
        ),
    )

    agent_log = {
        "agent": "RESPONSE_ORCHESTRATION_AGENT",
        "decision": f"{len(steps)}-step multi-department response plan created",
        "evidence_used": [
            f"Root cause: {chain_str}",
            f"Priority: {priority}",
            f"Departments involved: {', '.join(s['department_name'] for s in steps)}",
        ],
        "confidence": 0.85,
        "recommended_action": "REQUIRES HUMAN APPROVAL before execution",
    }

    return {
        "steps": steps,
        "rationale": rationale,
        "approved": False,
        "agent_log": agent_log,
    }
