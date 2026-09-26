"""
OmniCivic AI -- Escalation Agent
SLA/state-machine tracker with advance-demo-time hook.
"""

from typing import Dict, Any
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist() -> str:
    return datetime.now(IST).isoformat()


async def check_escalation(
    incident: Dict[str, Any],
    advance_hours: int = 0,
) -> Dict[str, Any]:
    """
    Escalation Agent: Check if an incident has breached its SLA deadline.
    If advance_hours > 0, simulate time advancement for demo purposes.

    Returns updated SLA info and new status if escalated.
    """
    incident_id = incident.get("incident_id", "")
    current_status = incident.get("status", "")
    sla = incident.get("sla", {})
    impact = incident.get("impact_score", {})
    priority = impact.get("priority", "MEDIUM")

    # SLA deadlines by priority (hours from incident creation)
    SLA_HOURS = {
        "CRITICAL": 12,
        "HIGH": 24,
        "MEDIUM": 48,
        "LOW": 72,
    }

    # Calculate SLA deadline if not set
    deadline_str = sla.get("deadline", "")
    if not deadline_str:
        created_at = incident.get("created_at", _now_ist())
        try:
            created_dt = datetime.fromisoformat(created_at)
        except (ValueError, TypeError):
            created_dt = datetime.now(IST)

        sla_hours = SLA_HOURS.get(priority, 48)
        deadline_dt = created_dt + timedelta(hours=sla_hours)
        deadline_str = deadline_dt.isoformat()

    # Determine current "simulated" time
    if advance_hours > 0:
        simulated_now = datetime.now(IST) + timedelta(hours=advance_hours)
    else:
        simulated_now = datetime.now(IST)

    # Check if SLA is breached
    try:
        deadline_dt = datetime.fromisoformat(deadline_str)
        # Make deadline timezone-aware if it isn't
        if deadline_dt.tzinfo is None:
            deadline_dt = deadline_dt.replace(tzinfo=IST)
        sla_breached = simulated_now > deadline_dt
    except (ValueError, TypeError):
        sla_breached = False

    # Determine escalation
    should_escalate = (
        sla_breached and
        current_status not in ("RESOLVED", "ESCALATED") and
        priority in ("CRITICAL", "HIGH")
    )

    new_status = current_status
    escalation_reason = ""

    if should_escalate:
        new_status = "ESCALATED"
        hours_overdue = (simulated_now - deadline_dt).total_seconds() / 3600
        escalation_reason = (
            f"SLA breached by {hours_overdue:.1f} hours. "
            f"Priority {priority} incident {incident_id} has not been resolved "
            f"within the {SLA_HOURS.get(priority, 48)}-hour deadline. "
            f"Escalating to senior management for immediate attention."
        )

    reminders_sent = sla.get("reminders_sent", 0)
    if should_escalate:
        reminders_sent += 1

    updated_sla = {
        "deadline": deadline_str,
        "reminders_sent": reminders_sent,
        "escalated": should_escalate or sla.get("escalated", False),
        "escalation_reason": escalation_reason or sla.get("escalation_reason", ""),
        "original_deadline": sla.get("original_deadline", deadline_str),
    }

    agent_log = {
        "agent": "ESCALATION_AGENT",
        "decision": (
            f"ESCALATED - SLA breached" if should_escalate
            else f"Within SLA - no escalation needed"
        ),
        "evidence_used": [
            f"Deadline: {deadline_str}",
            f"Current status: {current_status}",
            f"Priority: {priority}",
            f"{'Time advanced by ' + str(advance_hours) + ' hours (demo mode)' if advance_hours > 0 else 'Real-time check'}",
        ],
        "confidence": 1.0,
        "recommended_action": (
            "REQUIRES HUMAN REVIEW: Escalation to senior management"
            if should_escalate
            else "Continue monitoring"
        ),
    }

    return {
        "incident_id": incident_id,
        "new_status": new_status,
        "sla": updated_sla,
        "sla_breached": sla_breached,
        "escalated": should_escalate,
        "escalation_reason": escalation_reason,
        "agent_log": agent_log,
    }
