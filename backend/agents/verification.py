"""
OmniCivic AI -- Resolution Verification Agent
Verifies before/after photos, GPS, timestamps, new nearby complaints.
Two-attempt demo beat: mismatch -> fail -> correct evidence -> verify.
"""

import json
import os
from typing import Dict, Any, List

from tools.verification_tools import verify_resolution_evidence
from services.ai_service import generate_narrative

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _load_complaints() -> List[Dict]:
    path = os.path.join(DATA_DIR, "complaints.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("reports", [])


def _load_perception_lookup() -> dict:
    path = os.path.join(DATA_DIR, "perception_lookup.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def verify_resolution(incident: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolution Verification Agent: Verify whether a claimed resolution
    actually solved the problem.

    Checks:
    1. GPS location match (after photo GPS vs incident location)
    2. Image analysis (seed image lookup for MVP)
    3. New complaints post-resolution

    Outcomes (using neutral, non-accusatory language):
    - RESOLUTION_VERIFIED: Evidence confirms the issue has been addressed
    - LOCATION_MISMATCH: Evidence location does not match incident site
    - POSSIBLE_FAILED_RESOLUTION: Evidence suggests issue may persist

    Returns verification result with confidence and details.
    """
    resolution = incident.get("resolution", {})
    after_photo = resolution.get("after_photo", "")
    complaints = _load_complaints()

    # Step 1: Check if the after_photo is a known seed image
    lookup = _load_perception_lookup()
    after_perception = lookup.get(after_photo, {})

    # Step 2: Run verification tools (GPS, new complaints)
    tool_result = verify_resolution_evidence(incident, complaints)

    verification_result = tool_result["verification_result"]
    base_details = tool_result["verification_details"]
    confidence = tool_result["confidence"]

    # Step 3: For seed images, check if the image content matches the incident type
    if after_perception and verification_result == "RESOLUTION_VERIFIED":
        # Check if the "resolved" image shows the same issue type
        incident_types = [p.get("issue_type", "") for p in incident.get("perception_results", [])]
        after_type = after_perception.get("issue_type", "")

        # If the after photo shows a DIFFERENT issue type, it might be wrong location
        if after_type and after_type not in incident_types and after_perception.get("severity", "LOW") != "LOW":
            verification_result = "LOCATION_MISMATCH"
            confidence = 0.20
            base_details = (
                f"Resolution evidence image appears to show {after_type}, "
                f"which does not match the incident's issue types ({', '.join(incident_types)}). "
                "The submitted photo does not appear to correspond to this incident. "
                "Please submit evidence from the correct location. "
                "DO NOT CLOSE this incident."
            )

    # Step 4: Generate LLM narrative for the verification
    narrative = await generate_narrative(
        system_prompt=(
            "You are a resolution verification analyst. Explain the verification "
            "result in 2-3 sentences. Use neutral, non-accusatory language. "
            "Do not blame or accuse anyone. Focus on evidence."
        ),
        user_prompt=(
            f"Verification result: {verification_result}\n"
            f"Details: {base_details}\n"
            f"Confidence: {confidence}\n"
            f"After photo: {after_photo}\n\n"
            "Explain this verification result clearly and neutrally."
        ),
        fallback_text=base_details,
    )

    agent_log = {
        "agent": "RESOLUTION_VERIFICATION_AGENT",
        "decision": verification_result,
        "evidence_used": [
            f"After photo: {after_photo}",
            f"GPS check: {'PASS' if tool_result['location_check']['within_threshold'] else 'FAIL'}",
            f"Distance: {tool_result['location_check']['distance_m']}m",
            f"New complaints post-resolution: {len(tool_result.get('new_complaints', []))}",
        ],
        "confidence": confidence,
        "recommended_action": {
            "RESOLUTION_VERIFIED": "Incident can be closed. Risk level reduced.",
            "LOCATION_MISMATCH": "DO NOT CLOSE. Request correct evidence from resolution team.",
            "POSSIBLE_FAILED_RESOLUTION": "REQUIRES HUMAN REVIEW. Consider reopening incident.",
        }.get(verification_result, "Further investigation needed"),
    }

    return {
        "verification_result": verification_result,
        "verification_details": narrative,
        "confidence": confidence,
        "location_check": tool_result["location_check"],
        "new_complaints": tool_result.get("new_complaints", []),
        "agent_log": agent_log,
    }
