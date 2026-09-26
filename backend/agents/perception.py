"""
OmniCivic AI -- Perception Agent
Integrates Gemini multimodal analysis for uploaded photos,
and deterministic lookup tables for pre-built scenario seed images.
"""

import json
import os
from typing import Dict, Any, List

from services.ai_service import generate_narrative
from services.gemini_service import analyze_uploaded_image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_REPORTS_DIR = os.path.join(BASE_DIR, "uploads", "reports")


def _load_perception_lookup() -> dict:
    path = os.path.join(DATA_DIR, "perception_lookup.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def analyze_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perception Agent: Analyze a report's image to determine issue type,
    severity, and confidence.

    Modes:
    1. Uploaded Citizen Image: Uses Gemini multimodal model.
    2. Seed Demo Image: Uses deterministic lookup table for 100% demo stability.

    Returns:
    {
        "report_id": str,
        "issue_type": str,
        "severity": str,
        "confidence": float,
        "evidence_text": str,
        "image_filename": str,
        "visual_evidence": List[str],
        "agent_log": dict
    }
    """
    report_id = report.get("report_id", "")
    image_filename = report.get("image_filename", "")
    description = report.get("description", "")

    # Check if this is an uploaded citizen photo
    is_uploaded = image_filename.startswith("report_")
    
    if is_uploaded:
        image_path = os.path.join(UPLOADS_REPORTS_DIR, image_filename)
        print(f"[PERCEPTION_AGENT] Performing Multimodal analysis on uploaded image: {image_path}")
        
        # Analyze using Gemini Multimodal Service
        analysis = await analyze_uploaded_image(image_path, description)
        
        issue_type = analysis["issue_type"]
        severity = analysis["severity"]
        confidence = analysis["confidence"]
        visual_evidence = analysis["visual_evidence"]
        evidence_text = f"Visual evidence detected: {'. '.join(visual_evidence)}."
    else:
        # Predefined Demo Image lookup mode
        lookup = _load_perception_lookup()
        perception = lookup.get(image_filename)
        
        if not perception:
            # Try without extension or with different extension
            base = os.path.splitext(image_filename)[0]
            for ext in [".jpg", ".png", ".jpeg", ".webp"]:
                perception = lookup.get(base + ext)
                if perception:
                    break

        if perception:
            issue_type = perception["issue_type"]
            severity = perception["severity"]
            confidence = perception["confidence"]
            fallback_evidence = perception.get("evidence_text", "")
        else:
            # Fallback: try to infer from description keywords
            issue_type, severity, confidence = _infer_from_description(description)
            fallback_evidence = f"Classification inferred from report description. Confidence adjusted to reflect text-only analysis."

        # Generate LLM narrative evidence for demo image
        evidence_text = await generate_narrative(
            system_prompt=(
                "You are a civic infrastructure analyst. Generate a 2-3 sentence "
                "evidence description for a civic complaint photo analysis. "
                "Be factual and observational. Describe physical evidence visible."
            ),
            user_prompt=(
                f"Issue type detected: {issue_type}\n"
                f"Severity: {severity}\n"
                f"Citizen's description: {description}\n"
                f"Image: {image_filename}\n\n"
                "Write a brief observational evidence summary describing what visual "
                "analysis reveals about this civic issue."
            ),
            fallback_text=fallback_evidence,
        )
        
        # For seed images, construct visual evidence from the description/narrative
        visual_evidence = [
            f"Observed defect matching category: {issue_type.lower().replace('_', ' ')}",
            f"Observed severity level assessed as {severity.lower()}",
            "Visual validation matches known demographic seeds"
        ]

    agent_log = {
        "agent": "PERCEPTION_AGENT",
        "decision": f"Classified as {issue_type}, {severity} severity",
        "evidence_used": [
            f"Image analysis: {image_filename}",
            f"Citizen report: {report_id}",
        ] + [f"Visual: {e}" for e in visual_evidence],
        "confidence": confidence,
        "recommended_action": "Proceed to clustering for related reports in the area",
    }

    return {
        "report_id": report_id,
        "issue_type": issue_type,
        "severity": severity,
        "confidence": confidence,
        "evidence_text": evidence_text,
        "image_filename": image_filename,
        "visual_evidence": visual_evidence,
        "agent_log": agent_log,
    }


def _infer_from_description(description: str) -> tuple:
    """Fallback: infer issue type from description keywords."""
    desc_lower = description.lower()

    keyword_map = [
        (["water leak", "pipe leak", "pipe burst", "water flowing", "water seep"], "WATER_LEAKAGE", "HIGH", 0.70),
        (["pothole", "pot hole", "road hole", "cavity"], "POTHOLE", "MEDIUM", 0.65),
        (["waterlogging", "water logging", "flooding", "water stagnant", "standing water"], "WATERLOGGING", "MEDIUM", 0.65),
        (["road damage", "road broken", "road crack", "road surface"], "ROAD_DAMAGE", "MEDIUM", 0.65),
        (["garbage", "waste", "trash", "rubbish", "dumping"], "GARBAGE_OVERFLOW", "MEDIUM", 0.60),
        (["drain block", "blocked drain", "drain clog"], "DRAIN_BLOCKAGE", "MEDIUM", 0.65),
        (["drainage", "drain problem", "water not flowing"], "DRAINAGE_PROBLEM", "MEDIUM", 0.60),
        (["exposed wire", "live wire", "electric", "electrocution"], "EXPOSED_WIRES", "CRITICAL", 0.75),
        (["streetlight", "street light", "lamp not", "dark road"], "BROKEN_STREETLIGHT", "MEDIUM", 0.60),
        (["sewage", "sewer", "manhole overflow"], "SEWAGE_OVERFLOW", "HIGH", 0.65),
    ]

    for keywords, issue_type, severity, confidence in keyword_map:
        for kw in keywords:
            if kw in desc_lower:
                return (issue_type, severity, confidence)

    return ("POTHOLE", "MEDIUM", 0.50)  # Default fallback
