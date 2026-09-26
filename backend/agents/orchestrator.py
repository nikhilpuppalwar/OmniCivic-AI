"""
OmniCivic AI -- Orchestrator
Central pipeline controller. Sole writer of IncidentContext to disk.

Pipeline: OBSERVE -> UNDERSTAND -> CONNECT -> INVESTIGATE -> PRIORITIZE ->
          PLAN -> ACT/RECOMMEND -> TRACK -> VERIFY -> REPLAN/ESCALATE
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

from agents.perception import analyze_report
from agents.clustering import find_cluster
from agents.incident import detect_incident
from agents.root_cause import investigate_root_cause
from agents.impact import assess_impact
from agents.response import create_response_plan
from agents.filing import file_complaint

IST = timezone(timedelta(hours=5, minutes=30))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _now_ist() -> str:
    return datetime.now(IST).isoformat()


def _load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(filename: str, data: dict):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _append_agent_log(entry: dict):
    """Append an agent log entry to the centralized log."""
    entry["timestamp"] = _now_ist()
    logs = _load_json("agent_logs.json")
    if "logs" not in logs:
        logs["logs"] = []
    logs["logs"].append(entry)
    logs["total"] = len(logs["logs"])
    _save_json("agent_logs.json", logs)


def _next_incident_id() -> str:
    data = _load_json("incidents.json")
    incidents = data.get("incidents", [])
    if not incidents:
        return "INC-2026-001"
    max_num = 0
    for inc in incidents:
        try:
            num = int(inc["incident_id"].split("-")[-1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            pass
    return f"INC-2026-{max_num + 1:03d}"


async def run_full_pipeline(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the full agent pipeline on a new report.

    Pipeline stages:
    1. PERCEPTION: Analyze the report image/description
    2. CLUSTERING: Find nearby related reports
    3. PERCEPTION (batch): Analyze all clustered reports
    4. INCIDENT DETECTION: Classify the cluster
    5. ROOT CAUSE: Find causal chain
    6. IMPACT: Score civic impact
    7. RESPONSE: Create department response plan
    8. FILING: Create formal complaint record

    Returns the complete pipeline result with all agent outputs.
    """
    report_id = report.get("report_id", "")
    pipeline_result = {
        "report_id": report_id,
        "stages": {},
        "agent_logs": [],
        "incident_id": None,
    }

    # ── Stage 1: PERCEPTION ──────────────────────────────────────────────
    perception_result = await analyze_report(report)
    _append_agent_log(perception_result["agent_log"])
    pipeline_result["stages"]["perception"] = {
        "status": "complete",
        "result": {
            "report_id": perception_result["report_id"],
            "issue_type": perception_result["issue_type"],
            "severity": perception_result["severity"],
            "confidence": perception_result["confidence"],
            "evidence_text": perception_result["evidence_text"],
            "visual_evidence": perception_result.get("visual_evidence", []),
        },
    }
    pipeline_result["agent_logs"].append(perception_result["agent_log"])

    # ── Stage 2: CLUSTERING ──────────────────────────────────────────────
    cluster_result = await find_cluster(report)
    _append_agent_log(cluster_result["agent_log"])
    cluster = cluster_result["cluster"]
    pipeline_result["stages"]["clustering"] = {
        "status": "complete",
        "result": {
            "cluster_size": cluster["count"],
            "radius_m": cluster["radius_m"],
            "report_ids": cluster["report_ids"],
            "reasoning": cluster_result["reasoning"],
        },
    }
    pipeline_result["agent_logs"].append(cluster_result["agent_log"])

    # ── Stage 3: BATCH PERCEPTION (for clustered reports) ────────────────
    all_perception_results = [perception_result]
    cluster_reports = [report]  # Include target report

    for clustered_report in cluster["reports"]:
        p_result = await analyze_report(clustered_report)
        all_perception_results.append(p_result)
        cluster_reports.append(clustered_report)

    pipeline_result["stages"]["batch_perception"] = {
        "status": "complete",
        "result": {
            "analyzed_count": len(all_perception_results),
            "issue_types": list(set(p["issue_type"] for p in all_perception_results)),
        },
    }

    # ── Stage 4: INCIDENT DETECTION ──────────────────────────────────────
    detection_result = await detect_incident(
        report=report,
        perception_result=perception_result,
        cluster=cluster,
        all_perception_results=all_perception_results,
    )
    _append_agent_log(detection_result["agent_log"])
    pipeline_result["stages"]["incident_detection"] = {
        "status": "complete",
        "result": {
            "classification": detection_result["classification"],
            "issue_types": detection_result["issue_types"],
            "reasoning": detection_result["reasoning"],
            "confidence": detection_result["confidence"],
        },
    }
    pipeline_result["agent_logs"].append(detection_result["agent_log"])

    # Only create a full incident if connected reports detected
    if "CONNECTED" not in detection_result["classification"]:
        # Update report status
        _update_report_status(report_id, "UNDER_REVIEW")
        pipeline_result["stages"]["summary"] = {
            "status": "complete",
            "classification": detection_result["classification"],
            "message": "Report classified as independent or duplicate. No incident created.",
        }
        return pipeline_result

    # ── Create Incident ──────────────────────────────────────────────────
    incident_id = _next_incident_id()
    pipeline_result["incident_id"] = incident_id

    connected_report_ids = [report_id] + cluster["report_ids"]

    # Initialize incident context
    incident = {
        "incident_id": incident_id,
        "status": "UNDER_REVIEW",
        "classification": detection_result["classification"],
        "created_at": _now_ist(),
        "updated_at": _now_ist(),
        "connected_reports": connected_report_ids,
        "cluster": {
            "radius_m": cluster["radius_m"],
            "time_window_days": cluster["time_window_days"],
            "center_lat": cluster["center_lat"],
            "center_lon": cluster["center_lon"],
            "report_count": len(connected_report_ids),
        },
        "perception_results": [
            {
                "report_id": p["report_id"],
                "issue_type": p["issue_type"],
                "severity": p["severity"],
                "confidence": p["confidence"],
                "evidence_text": p["evidence_text"],
                "image_filename": p.get("image_filename", ""),
                "visual_evidence": p.get("visual_evidence", []),
            }
            for p in all_perception_results
        ],
        "root_cause": {},
        "impact_score": {},
        "response_plan": {},
        "resolution": {},
        "sla": {},
        "agent_log": [],
    }

    # ── Stage 5, 6 & 7: AGENTIC REASONING LOOP (Root Cause, Impact, Response) ─
    from agents.reasoning_agent import run_agentic_reasoning

    reasoning_output = await run_agentic_reasoning(
        primary_report=report,
        cluster_reports=cluster["reports"],
        cluster_type=detection_result["classification"],
    )

    reasoning_mode = reasoning_output.get("reasoning_mode", "deterministic_fallback")
    rc_data = reasoning_output.get("root_cause", {})
    impact_data = reasoning_output.get("impact_score", {})
    plan_data = reasoning_output.get("response_plan", {})
    tools_used = reasoning_output.get("tools_used", [])
    tool_traces = reasoning_output.get("tool_traces", [])
    reasoning_notes = reasoning_output.get("reasoning_notes", "")

    # Populate incident fields
    incident["reasoning_mode"] = reasoning_mode
    incident["tools_used"] = tools_used
    incident["tool_traces"] = tool_traces

    nearby_sites = reasoning_output.get("nearby_sites") or rc_data.get("nearby_sites", [])

    incident["nearby_sites"] = nearby_sites
    incident["root_cause"] = {
        "hypothesis": rc_data.get("hypothesis", ""),
        "confidence": rc_data.get("confidence", 0.85),
        "chain": rc_data.get("chain", []),
        "disclaimer": rc_data.get(
            "disclaimer",
            "AI-generated civic incident hypothesis. Physical inspection recommended.",
        ),
        "tools_used": tools_used,
        "reasoning_notes": reasoning_notes,
        "nearby_sites": nearby_sites,
    }


    incident["impact_score"] = {
        "score": impact_data.get("score", 75),
        "priority": impact_data.get("priority", "HIGH"),
        "breakdown": impact_data.get("factor_breakdown", impact_data.get("breakdown", {})),
        "explanation": impact_data.get("explanation", ""),
        "tools_used": tools_used,
    }

    incident["response_plan"] = {
        "steps": plan_data.get("steps", []),
        "rationale": reasoning_notes,
        "approved": False,
        "approved_by": "",
        "approved_at": "",
    }

    # Record agent logs for the pipeline result
    rc_agent_log = {
        "agent": "Root-Cause Agent",
        "timestamp": _now_ist(),
        "message": f"Formed cascade hypothesis [{reasoning_mode}]: {rc_data.get('hypothesis')}",
        "decision": "CASCADE_CHAIN_IDENTIFIED",
        "evidence_used": [f"Tools used: {', '.join(tools_used)}", reasoning_notes],
        "confidence": rc_data.get("confidence", 0.85),
        "recommended_action": "Sequence repairs starting at root node",
    }
    _append_agent_log(rc_agent_log)
    pipeline_result["stages"]["root_cause"] = {
        "status": "complete",
        "result": {
            "chain": rc_data.get("chain", []),
            "confidence": rc_data.get("confidence", 0.85),
            "hypothesis": rc_data.get("hypothesis", ""),
            "disclaimer": rc_data.get("disclaimer", ""),
            "reasoning_mode": reasoning_mode,
            "tools_used": tools_used,
        },
    }
    pipeline_result["agent_logs"].append(rc_agent_log)

    impact_agent_log = {
        "agent": "Civic Impact Agent",
        "timestamp": _now_ist(),
        "message": f"Calculated civic threat score {impact_data.get('score')}/100 ({impact_data.get('priority')})",
        "decision": f"PRIORITY_{impact_data.get('priority')}",
        "evidence_used": [impact_data.get("explanation", "")],
        "confidence": 0.90,
        "recommended_action": f"Set SLA deadline according to {impact_data.get('priority')} tier",
    }
    _append_agent_log(impact_agent_log)
    pipeline_result["stages"]["impact"] = {
        "status": "complete",
        "result": {
            "score": impact_data.get("score"),
            "priority": impact_data.get("priority"),
            "breakdown": impact_data.get("factor_breakdown", impact_data.get("breakdown", {})),
            "explanation": impact_data.get("explanation"),
            "reasoning_mode": reasoning_mode,
        },
    }
    pipeline_result["agent_logs"].append(impact_agent_log)

    response_agent_log = {
        "agent": "Response Agent",
        "timestamp": _now_ist(),
        "message": f"Designed {len(plan_data.get('steps', []))}-step sequenced response plan across departments.",
        "decision": "PLAN_GENERATED",
        "evidence_used": ["Topological sort of department execution dependencies"],
        "confidence": 0.95,
        "recommended_action": "Await authority officer approval before dispatching field teams",
    }
    _append_agent_log(response_agent_log)
    pipeline_result["stages"]["response"] = {
        "status": "complete",
        "result": {
            "steps": plan_data.get("steps", []),
            "rationale": reasoning_notes,
            "approved": False,
        },
    }
    pipeline_result["agent_logs"].append(response_agent_log)


    # ── Stage 8: FILING ──────────────────────────────────────────────────
    filing_result = await file_complaint(
        incident=incident,
        perception_results=all_perception_results,
        impact=incident["impact_score"],
    )
    _append_agent_log(filing_result["agent_log"])
    pipeline_result["stages"]["filing"] = {
        "status": "complete",
        "result": filing_result["filing"],
    }
    pipeline_result["agent_logs"].append(filing_result["agent_log"])

    # ── Set SLA deadline ─────────────────────────────────────────────────
    SLA_HOURS = {"CRITICAL": 12, "HIGH": 24, "MEDIUM": 48, "LOW": 72}
    sla_hours = SLA_HOURS.get(incident["impact_score"].get("priority", "HIGH"), 48)
    created_dt = datetime.now(IST)
    deadline_dt = created_dt + timedelta(hours=sla_hours)
    incident["sla"] = {
        "deadline": deadline_dt.isoformat(),
        "reminders_sent": 0,
        "escalated": False,
        "escalation_reason": "",
        "original_deadline": deadline_dt.isoformat(),
    }


    # ── Write incident to disk (Orchestrator is sole writer) ─────────────
    incidents_data = _load_json("incidents.json")
    incidents_data["incidents"].append(incident)
    incidents_data["total"] = len(incidents_data["incidents"])
    _save_json("incidents.json", incidents_data)

    # ── Update linked report statuses ────────────────────────────────────
    for rid in connected_report_ids:
        _update_report_status(rid, "LINKED_TO_INCIDENT", incident_id)

    pipeline_result["stages"]["summary"] = {
        "status": "complete",
        "incident_id": incident_id,
        "classification": detection_result["classification"],
        "impact_score": incident["impact_score"].get("score", 0),
        "priority": incident["impact_score"].get("priority", "HIGH"),
        "response_steps": len(incident["response_plan"].get("steps", [])),
        "message": f"Incident {incident_id} created with {len(connected_report_ids)} connected reports.",
    }


    return pipeline_result


async def analyze_existing_incident(incident: Dict[str, Any]) -> Dict[str, Any]:
    """Re-analyze an existing incident (for updates)."""
    # This is a simplified version for re-analysis
    return {
        "incident_id": incident["incident_id"],
        "status": incident["status"],
        "message": "Incident analysis refreshed.",
    }


def _update_report_status(
    report_id: str,
    status: str,
    incident_id: str = None,
):
    """Update a report's status and linked incident."""
    data = _load_json("complaints.json")
    for r in data.get("reports", []):
        if r["report_id"] == report_id:
            r["status"] = status
            if incident_id:
                r["linked_incident_id"] = incident_id
            break
    _save_json("complaints.json", data)
