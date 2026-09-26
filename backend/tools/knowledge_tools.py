"""
OmniCivic AI -- Knowledge Tools
Department lookup and dependency graph traversal for root cause analysis.
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple
from collections import deque

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_departments() -> dict:
    return _load_json("departments.json")


def get_dependencies() -> dict:
    return _load_json("civic_dependencies.json")


def get_department_for_issue(issue_type: str) -> List[Dict[str, Any]]:
    """Look up which department(s) handle a given issue type."""
    dept_data = get_departments()
    issue_map = dept_data.get("issue_to_departments", {})
    departments = dept_data.get("departments", {})

    dept_codes = issue_map.get(issue_type, [])
    result = []
    for code in dept_codes:
        if code in departments:
            dept = dict(departments[code])
            dept["code"] = code
            result.append(dept)
    return result


def get_department_dependencies() -> Dict[str, Dict]:
    """Get the department execution dependency map."""
    dept_data = get_departments()
    return dept_data.get("department_dependencies", {})


def find_causal_chain(issue_types: List[str]) -> Dict[str, Any]:
    """
    Walk the civic_dependencies.json graph to find the most likely causal chain
    connecting the given issue types.

    Returns:
    - chain: ordered list of issue types from root cause to final effect
    - confidence: overall chain confidence (product of edge confidences)
    - evidence: list of mechanism descriptions
    """
    deps = get_dependencies()
    dep_graph = deps.get("dependencies", {})

    if len(issue_types) <= 1:
        return {
            "chain": issue_types,
            "confidence": 0.5,
            "evidence": ["Single issue type - no causal chain to analyze"],
        }

    # Build adjacency list with confidences
    adjacency: Dict[str, List[Tuple[str, float, str]]] = {}
    for source, info in dep_graph.items():
        adjacency[source] = []
        for edge in info.get("can_cause", []):
            adjacency[source].append((
                edge["target"],
                edge["confidence"],
                edge["mechanism"],
            ))

    # Find the best chain connecting all issue types using BFS/DFS
    unique_types = list(set(issue_types))
    best_chain = _find_best_chain(adjacency, unique_types)

    if best_chain:
        chain_types = [step["type"] for step in best_chain]
        confidence = 1.0
        for step in best_chain:
            confidence *= step.get("edge_confidence", 1.0)
        confidence = round(confidence, 2)

        # Adjust confidence based on how many types are covered
        coverage = len(set(chain_types) & set(unique_types)) / len(unique_types)
        adjusted_confidence = round(confidence * coverage, 2)

        evidence = [step.get("mechanism", "") for step in best_chain if step.get("mechanism")]

        return {
            "chain": chain_types,
            "confidence": max(adjusted_confidence, 0.3),
            "evidence": evidence,
        }

    # Fallback: just list the types with low confidence
    return {
        "chain": unique_types,
        "confidence": 0.3,
        "evidence": ["No direct causal path found between all issue types. Proximity and timing suggest possible connection."],
    }


def _find_best_chain(
    adjacency: Dict[str, List[Tuple[str, float, str]]],
    target_types: List[str],
) -> List[Dict[str, Any]]:
    """
    Find the best chain through the dependency graph that covers the most target types.
    Uses BFS from each potential root cause.
    """
    best_chain = []
    best_coverage = 0
    best_confidence = 0

    target_set = set(target_types)

    for start in target_types:
        if start not in adjacency:
            continue

        # BFS from this starting point
        chain = [{"type": start, "edge_confidence": 1.0, "mechanism": "Root cause"}]
        visited = {start}
        queue = deque([(start, chain)])

        current_best = list(chain)

        while queue:
            current, current_chain = queue.popleft()

            for neighbor, conf, mechanism in adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_chain = current_chain + [{
                        "type": neighbor,
                        "edge_confidence": conf,
                        "mechanism": mechanism,
                    }]

                    coverage = len(set(n["type"] for n in new_chain) & target_set)
                    if coverage > len(set(n["type"] for n in current_best) & target_set):
                        current_best = new_chain

                    queue.append((neighbor, new_chain))

        coverage = len(set(n["type"] for n in current_best) & target_set)
        chain_conf = 1.0
        for step in current_best:
            chain_conf *= step["edge_confidence"]

        if coverage > best_coverage or (coverage == best_coverage and chain_conf > best_confidence):
            best_chain = current_best
            best_coverage = coverage
            best_confidence = chain_conf

    return best_chain


def get_response_order(issue_types: List[str]) -> List[Dict[str, Any]]:
    """
    Determine the correct department response order based on dependencies.
    Returns ordered list of department actions.
    """
    dept_data = get_departments()
    issue_map = dept_data.get("issue_to_departments", {})
    departments = dept_data.get("departments", {})
    dept_deps = dept_data.get("department_dependencies", {})

    # Collect all required departments
    required_depts = set()
    dept_to_issues: Dict[str, List[str]] = {}

    for issue in issue_types:
        for dept_code in issue_map.get(issue, []):
            required_depts.add(dept_code)
            if dept_code not in dept_to_issues:
                dept_to_issues[dept_code] = []
            dept_to_issues[dept_code].append(issue)

    # Topological sort based on dependencies
    ordered = _topological_sort(required_depts, dept_deps)

    result = []
    for i, dept_code in enumerate(ordered):
        dept_info = departments.get(dept_code, {})
        issues = dept_to_issues.get(dept_code, [])
        dep_info = dept_deps.get(dept_code, {})

        result.append({
            "step_number": i + 1,
            "department": dept_code,
            "department_name": dept_info.get("name", dept_code),
            "issues": issues,
            "action": f"Address {', '.join(issues)} issues",
            "reason": dep_info.get("reason", "Required for issue resolution"),
            "depends_on": dep_info.get("must_complete_after", []),
            "sla_hours": dept_info.get("sla_hours", {}),
            "resources": dept_info.get("resources", []),
        })

    return result


def _topological_sort(
    nodes: set,
    dependencies: Dict[str, Dict],
) -> List[str]:
    """Topological sort of departments based on dependency order."""
    # Build in-degree count
    in_degree = {n: 0 for n in nodes}
    adj: Dict[str, List[str]] = {n: [] for n in nodes}

    for node in nodes:
        must_after = dependencies.get(node, {}).get("must_complete_after", [])
        for dep in must_after:
            if dep in nodes:
                adj[dep].append(node)
                in_degree[node] += 1

    # Kahn's algorithm
    queue = deque([n for n in nodes if in_degree[n] == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in adj.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Add any remaining (in case of cycles)
    for n in nodes:
        if n not in result:
            result.append(n)

    return result
