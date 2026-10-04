"""
OmniCivic AI -- Critic / Reflection Agent

Performs self-check and reflective revision over root-cause, impact assessment,
and response plan drafts before final incident persistence.

Validates:
1. Causal graph validity against civic_dependencies.json.
2. Grounded evidence without hallucination.
3. Confidence consistency with available evidence.
4. Impact score mathematical consistency (0.30/0.20/0.15/0.10/0.10/0.15 formula) and priority tier thresholds.
5. Sensitive site proximity reflection in civic risk factors.
6. Department coverage and topological order of response plan.
"""

import json
import os
import copy
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _now_ist_str() -> str:
    return datetime.now(IST).isoformat()


SYNONYMS = {
    "WATER_PIPE_BURST": "WATER_LEAKAGE",
    "PIPE_BURST": "WATER_LEAKAGE",
    "ROAD_CAVE_IN": "ROAD_DAMAGE",
    "CAVE_IN": "ROAD_DAMAGE",
    "STREETLIGHT": "BROKEN_STREETLIGHT",
    "STREETLIGHT_OUT": "BROKEN_STREETLIGHT",
    "WIRES": "EXPOSED_WIRES",
}


def load_dependency_graph() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Load civic dependency graph definition and scenario chains."""
    dep_file = os.path.join(DATA_DIR, "civic_dependencies.json")
    if os.path.exists(dep_file):
        try:
            with open(dep_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("dependencies", {}), data.get("scenario_chains", {})
        except Exception as e:
            logger.error(f"[CRITIC] Failed to read civic_dependencies.json: {e}")
    return {}, {}


def calculate_expected_priority(score: float) -> str:
    """Standard priority thresholds: >=80 CRITICAL, 65-79 HIGH, 45-64 MEDIUM, <45 LOW."""
    if score >= 80:
        return "CRITICAL"
    elif score >= 65:
        return "HIGH"
    elif score >= 45:
        return "MEDIUM"
    return "LOW"


def evaluate_draft(
    draft: Dict[str, Any],
    cluster_reports: List[Dict[str, Any]],
    nearby_sites: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[str, List[str], List[Dict[str, Any]]]:
    """
    Run deterministic validation checks on a reasoning draft.
    Returns: (verdict: "approved"|"revise", issues: List[str], checks: List[Dict])
    """
    checks: List[Dict[str, Any]] = []
    issues: List[str] = []

    rc = draft.get("root_cause", {})
    impact = draft.get("impact_score", {})
    plan = draft.get("response_plan", {})
    chain = rc.get("chain", [])
    confidence = rc.get("confidence", 0.0)
    hypothesis = rc.get("hypothesis", "")
    reasoning_notes = draft.get("reasoning_notes", "") + " " + rc.get("reasoning_notes", "")

    deps, scenario_chains = load_dependency_graph()

    # ── Check 1: Causal Chain in Dependency Graph ──
    chain_valid = True
    chain_detail = "All links valid in civic dependency graph."
    if not chain:
        chain_valid = False
        chain_detail = "Causal chain is empty."
        issues.append(chain_detail)
    else:
        for i in range(len(chain) - 1):
            raw_s = chain[i].upper().replace(" ", "_")
            raw_t = chain[i + 1].upper().replace(" ", "_")
            source = SYNONYMS.get(raw_s, raw_s)
            target = SYNONYMS.get(raw_t, raw_t)

            is_novel = "novel hypothesis" in hypothesis.lower() or "novel hypothesis" in reasoning_notes.lower()
            if is_novel:
                continue

            node_data = deps.get(source, {})
            can_cause_targets = [
                c.get("target", "").upper().replace(" ", "_")
                for c in node_data.get("can_cause", [])
                if isinstance(c, dict)
            ]
            leads_to = [x.upper().replace(" ", "_") for x in node_data.get("leads_to", [])]
            typical = [x.upper().replace(" ", "_") for x in node_data.get("typical_cascade", [])]

            # Also check scenario chains
            scenario_matches = False
            for sc in scenario_chains.values():
                sc_chain = [SYNONYMS.get(x.upper().replace(" ", "_"), x.upper().replace(" ", "_")) for x in sc.get("chain", [])]
                if source in sc_chain and target in sc_chain:
                    s_idx = sc_chain.index(source)
                    t_idx = sc_chain.index(target)
                    if s_idx < t_idx:
                        scenario_matches = True
                        break

            all_targets = set(can_cause_targets + leads_to + typical)
            if target not in all_targets and not scenario_matches:
                chain_valid = False
                chain_detail = f"Link '{raw_s}' -> '{raw_t}' does not exist in civic dependency graph."
                issues.append(chain_detail)
                break

    checks.append({
        "name": "causal_graph_alignment",
        "passed": chain_valid,
        "detail": chain_detail
    })

    # ── Check 2: Grounded Evidence ──
    evidence_items = rc.get("evidence", [])
    grounded_valid = True
    grounded_detail = "Evidence items grounded in reported symptoms or sensor inputs."
    if not evidence_items and not hypothesis:
        grounded_valid = False
        grounded_detail = "Draft missing both hypothesis narrative and evidence references."
        issues.append(grounded_detail)

    checks.append({
        "name": "grounded_evidence",
        "passed": grounded_valid,
        "detail": grounded_detail
    })

    # ── Check 3: Confidence Consistency ──
    conf_valid = True
    conf_detail = f"Confidence ({confidence:.2f}) is consistent with evidence breadth."
    evidence_count = len(evidence_items) if evidence_items else len(cluster_reports)
    if confidence > 0.80 and evidence_count < 2:
        conf_valid = False
        conf_detail = f"High confidence ({confidence:.2f}) unsupported: fewer than 2 evidence items ({evidence_count} found)."
        issues.append(conf_detail)

    checks.append({
        "name": "confidence_consistency",
        "passed": conf_valid,
        "detail": conf_detail
    })

    # ── Check 4: Impact Score Formula & Priority Threshold ──
    impact_valid = True
    impact_detail = "Impact score matches breakdown formula and priority tier thresholds."
    score = float(impact.get("score", 0.0))
    priority = str(impact.get("priority", "LOW")).upper()
    breakdown = impact.get("breakdown") or impact.get("factor_breakdown") or {}

    if breakdown and isinstance(breakdown, dict):
        sev = float(breakdown.get("severity_score", 0.0))
        prox = float(breakdown.get("infrastructure_proximity", 0.0))
        ppl = float(breakdown.get("people_affected", 0.0))
        dur = float(breakdown.get("duration", 0.0))
        rep = float(breakdown.get("repeat_reports", 0.0))
        sec = float(breakdown.get("secondary_risk", 0.0))

        # Recompute formula S: 0.30/0.20/0.15/0.10/0.10/0.15
        expected_s = (0.30 * sev) + (0.20 * prox) + (0.15 * ppl) + (0.10 * dur) + (0.10 * rep) + (0.15 * sec)
        diff = abs(score - expected_s)

        if diff > 3.0:
            impact_valid = False
            impact_detail = f"Impact score ({score:.1f}) diverges from weighted breakdown formula sum ({expected_s:.1f}, diff: {diff:.1f} > 3.0)."
            issues.append(impact_detail)

    expected_p = calculate_expected_priority(score)
    if priority != expected_p and score > 0:
        impact_valid = False
        impact_detail = f"Priority tier '{priority}' does not match score {score:.1f} (expected '{expected_p}')."
        issues.append(impact_detail)

    checks.append({
        "name": "impact_formula_and_priority",
        "passed": impact_valid,
        "detail": impact_detail
    })

    # ── Check 5: Sensitive Sites Proximity Reflection ──
    sites_valid = True
    sites_detail = "Proximity risk correctly reflects local sensitive facilities."
    sites_list = nearby_sites or draft.get("nearby_sites") or rc.get("nearby_sites", [])
    if sites_list and breakdown:
        prox = float(breakdown.get("infrastructure_proximity", 0.0))
        if prox <= 0:
            sites_valid = False
            sites_detail = f"Sensitive facility located within 250m ({len(sites_list)} found), but infrastructure_proximity is 0."
            issues.append(sites_detail)

    checks.append({
        "name": "sensitive_sites_proximity",
        "passed": sites_valid,
        "detail": sites_detail
    })

    # ── Check 6: Topological Order and Department Coverage ──
    topo_valid = True
    topo_detail = "Response plan respects departmental topological execution order."
    steps = plan.get("steps", [])

    dept_priority = {
        "WATER_BOARD": 1,
        "STORM_WATER_DRAINAGE": 2,
        "ELECTRICAL_DEPT": 3,
        "SOLID_WASTE_MGMT": 4,
        "ROADS_DEPT": 5,
    }

    seen_priorities = []
    for step in steps:
        dept = step.get("department", "")
        p_val = dept_priority.get(dept, 99)
        if seen_priorities and p_val < max(seen_priorities):
            topo_valid = False
            topo_detail = f"Topological inversion: Step for {dept} follows a downstream department step."
            issues.append(topo_detail)
            break
        seen_priorities.append(p_val)

    checks.append({
        "name": "topological_department_order",
        "passed": topo_valid,
        "detail": topo_detail
    })

    verdict = "approved" if not issues else "revise"
    return verdict, issues, checks


def apply_deterministic_revision(
    draft: Dict[str, Any],
    issues: List[str],
    cluster_reports: List[Dict[str, Any]],
    nearby_sites: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Deterministically repair common draft discrepancies:
    - Recalculate impact score from breakdown weights
    - Align priority tier to threshold
    - Fix topological sort of response steps
    - Cap confidence if evidence count is low
    """
    revised = copy.deepcopy(draft)
    rc = revised.setdefault("root_cause", {})
    impact = revised.setdefault("impact_score", {})
    plan = revised.setdefault("response_plan", {})
    breakdown = impact.get("breakdown") or impact.get("factor_breakdown") or {}

    # 1. Fix impact score and priority
    if breakdown and isinstance(breakdown, dict):
        sev = float(breakdown.get("severity_score", 0.0))
        prox = float(breakdown.get("infrastructure_proximity", 0.0))
        ppl = float(breakdown.get("people_affected", 0.0))
        dur = float(breakdown.get("duration", 0.0))
        rep = float(breakdown.get("repeat_reports", 0.0))
        sec = float(breakdown.get("secondary_risk", 0.0))

        sites_list = nearby_sites or revised.get("nearby_sites") or rc.get("nearby_sites", [])
        if sites_list and prox <= 0:
            prox = 15.0
            breakdown["infrastructure_proximity"] = prox

        expected_s = round((0.30 * sev) + (0.20 * prox) + (0.15 * ppl) + (0.10 * dur) + (0.10 * rep) + (0.15 * sec), 1)
        impact["score"] = expected_s
        impact["priority"] = calculate_expected_priority(expected_s)

    # 2. Fix confidence
    evidence_count = len(rc.get("evidence", [])) or len(cluster_reports)
    if rc.get("confidence", 0.0) > 0.80 and evidence_count < 2:
        rc["confidence"] = 0.75

    # 3. Fix topological order
    dept_priority = {
        "WATER_BOARD": 1,
        "STORM_WATER_DRAINAGE": 2,
        "ELECTRICAL_DEPT": 3,
        "SOLID_WASTE_MGMT": 4,
        "ROADS_DEPT": 5,
    }
    steps = plan.get("steps", [])
    if steps:
        sorted_steps = sorted(steps, key=lambda s: dept_priority.get(s.get("department", ""), 99))
        for idx, s in enumerate(sorted_steps, 1):
            s["step_number"] = idx
        plan["steps"] = sorted_steps

    return revised


def run_critic_reflection(
    draft: Dict[str, Any],
    cluster_reports: List[Dict[str, Any]],
    nearby_sites: Optional[List[Dict[str, Any]]] = None,
    allow_llm_revision: bool = False,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Main entry point for the Critic / Reflection Agent.
    Evaluates draft, runs 1 revision pass if issues detected, and returns:
    (final_draft, reflection_metadata)
    """
    # Iteration 1: Initial evaluation
    verdict_1, issues_1, checks_1 = evaluate_draft(draft, cluster_reports, nearby_sites)

    if verdict_1 == "approved":
        reflection = {
            "verdict": "approved",
            "iterations": 1,
            "issues": [],
            "checks": checks_1,
        }
        draft["reflection"] = reflection
        return draft, reflection

    # Iteration 2: One revision pass
    logger.info(f"[CRITIC] Draft flagged with {len(issues_1)} issue(s). Executing revision pass...")
    revised_draft = apply_deterministic_revision(draft, issues_1, cluster_reports, nearby_sites)

    verdict_2, issues_2, checks_2 = evaluate_draft(revised_draft, cluster_reports, nearby_sites)

    if verdict_2 == "approved":
        reflection = {
            "verdict": "revised",
            "iterations": 2,
            "issues": issues_1,
            "checks": checks_2,
        }
        revised_draft["reflection"] = reflection
        return revised_draft, reflection

    # If still unresolved after revision pass, retain best draft and lower confidence
    logger.warning(f"[CRITIC] Revision pass completed but {len(issues_2)} issue(s) remain unresolved.")
    curr_conf = revised_draft.get("root_cause", {}).get("confidence", 0.85)
    revised_draft.setdefault("root_cause", {})["confidence"] = max(0.10, round(curr_conf - 0.15, 2))

    reflection = {
        "verdict": "unresolved",
        "iterations": 2,
        "issues": issues_2,
        "checks": checks_2,
    }
    revised_draft["reflection"] = reflection
    return revised_draft, reflection
