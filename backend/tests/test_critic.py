"""
Unit tests for Critic / Reflection Agent (backend/agents/critic.py).

Verifies:
1. Approved verdict for a fully sound draft.
2. Flagging deliberately broken drafts (impact formula mismatch, invalid chain link, topological inversion).
3. Revision pass repairs mathematical mismatch and topological inversion.
4. Unresolved verdict properly drops confidence when an unfixable issue remains.
"""

import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from agents.critic import evaluate_draft, run_critic_reflection


def test_critic_approved_on_valid_draft():
    """Verify sound draft passes all critic checks on first iteration."""
    draft = {
        "root_cause": {
            "hypothesis": "Burst water main causing road cavitation.",
            "chain": ["WATER_PIPE_BURST", "ROAD_CAVE_IN"],
            "confidence": 0.85,
            "evidence": ["Pavement cracking reported", "Water pooling above sub-base"],
        },
        "impact_score": {
            "score": 67.5,
            "priority": "HIGH",
            "breakdown": {
                "severity_score": 70,       # 0.30 * 70 = 21.0
                "infrastructure_proximity": 60, # 0.20 * 60 = 12.0
                "people_affected": 70,      # 0.15 * 70 = 10.5
                "duration": 50,             # 0.10 * 50 = 5.0
                "repeat_reports": 40,       # 0.10 * 40 = 4.0
                "secondary_risk": 100,      # 0.15 * 100 = 15.0 -> Sum = 67.5
            }
        },
        "response_plan": {
            "steps": [
                {"step_number": 1, "department": "WATER_BOARD", "action": "Shut off supply valve"},
                {"step_number": 2, "department": "ROADS_DEPT", "action": "Fill and repave cavity"}
            ]
        }
    }

    cluster_reports = [{"report_id": "R1"}, {"report_id": "R2"}]
    verdict, issues, checks = evaluate_draft(draft, cluster_reports)

    assert verdict == "approved"
    assert len(issues) == 0
    assert all(c["passed"] for c in checks)


def test_critic_catches_broken_impact_score_and_revises():
    """
    Verify critic flags an impact score that diverges > 3.0 points from breakdown weights
    and revises it.
    """
    broken_draft = {
        "root_cause": {
            "hypothesis": "Burst pipe water leak",
            "chain": ["WATER_PIPE_BURST", "ROAD_CAVE_IN"],
            "confidence": 0.82,
            "evidence": ["Water pressure drop", "Visible depression"],
        },
        "impact_score": {
            # Intentionally claim score of 95 (CRITICAL) despite breakdown only summing to 40
            "score": 95.0,
            "priority": "CRITICAL",
            "breakdown": {
                "severity_score": 40,
                "infrastructure_proximity": 40,
                "people_affected": 40,
                "duration": 40,
                "repeat_reports": 40,
                "secondary_risk": 40,  # Expected S = 40.0, Priority = LOW
            }
        },
        "response_plan": {
            "steps": [
                {"step_number": 1, "department": "WATER_BOARD", "action": "Repair main valve"},
                {"step_number": 2, "department": "ROADS_DEPT", "action": "Resurface"}
            ]
        }
    }

    cluster_reports = [{"report_id": "R1"}, {"report_id": "R2"}]

    # Step 1: evaluate_draft must flag the mismatch
    verdict, issues, checks = evaluate_draft(broken_draft, cluster_reports)
    assert verdict == "revise"
    assert any("diverges from weighted breakdown" in iss for iss in issues)

    # Step 2: run_critic_reflection must trigger revision and repair the math
    final_draft, reflection = run_critic_reflection(broken_draft, cluster_reports)
    assert reflection["verdict"] == "revised"
    assert reflection["iterations"] == 2
    assert final_draft["impact_score"]["score"] == 40.0
    assert final_draft["impact_score"]["priority"] == "LOW"


def test_critic_catches_topological_inversion():
    """Verify critic flags road resurfacing ordered BEFORE water pipe repair."""
    broken_order_draft = {
        "root_cause": {
            "hypothesis": "Burst pipe water leak",
            "chain": ["WATER_PIPE_BURST", "ROAD_CAVE_IN"],
            "confidence": 0.80,
            "evidence": ["Ponding", "Cavitation"],
        },
        "impact_score": {
            "score": 50.0,
            "priority": "MEDIUM",
            "breakdown": {
                "severity_score": 50, "infrastructure_proximity": 50, "people_affected": 50,
                "duration": 50, "repeat_reports": 50, "secondary_risk": 50
            }
        },
        "response_plan": {
            # Inverted: Roads department scheduled before Water Board!
            "steps": [
                {"step_number": 1, "department": "ROADS_DEPT", "action": "Pave asphalt over road"},
                {"step_number": 2, "department": "WATER_BOARD", "action": "Excavate and fix broken water pipe"}
            ]
        }
    }

    cluster_reports = [{"report_id": "R1"}, {"report_id": "R2"}]
    verdict, issues, checks = evaluate_draft(broken_order_draft, cluster_reports)
    assert verdict == "revise"
    assert any("Topological inversion" in iss for iss in issues)

    # Reflection repairs topological order
    final_draft, reflection = run_critic_reflection(broken_order_draft, cluster_reports)
    assert reflection["verdict"] == "revised"
    steps = final_draft["response_plan"]["steps"]
    assert steps[0]["department"] == "WATER_BOARD"
    assert steps[1]["department"] == "ROADS_DEPT"


def test_critic_catches_unsupported_high_confidence():
    """Verify critic flags confidence > 0.8 with fewer than 2 evidence items."""
    thin_draft = {
        "root_cause": {
            "hypothesis": "Pothole on main lane",
            "chain": ["POTHOLE"],
            "confidence": 0.95,  # Unsound high confidence
            "evidence": ["Single vague citizen remark"],  # Only 1 item
        },
        "impact_score": {
            "score": 30.0,
            "priority": "LOW",
            "breakdown": {
                "severity_score": 30, "infrastructure_proximity": 30, "people_affected": 30,
                "duration": 30, "repeat_reports": 30, "secondary_risk": 30
            }
        },
        "response_plan": {
            "steps": [{"step_number": 1, "department": "ROADS_DEPT", "action": "Patch pothole"}]
        }
    }

    cluster_reports = [{"report_id": "R1"}]
    verdict, issues, checks = evaluate_draft(thin_draft, cluster_reports)
    assert verdict == "revise"
    assert any("High confidence" in iss for iss in issues)

    final_draft, reflection = run_critic_reflection(thin_draft, cluster_reports)
    assert final_draft["root_cause"]["confidence"] <= 0.80
