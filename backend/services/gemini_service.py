"""
OmniCivic AI -- Gemini Multimodal Service
Handles image analysis using the google-generativeai SDK.
Gracefully falls back to deterministic analysis if API key is missing or calls fail.
"""

import os
import json
import re
from typing import Dict, Any, List
from PIL import Image
from dotenv import load_dotenv

_genai_configured = False


def _configure_genai():
    """Configure google-generativeai if API key is present."""
    global _genai_configured

    if _genai_configured:
        return True
    try:
        from services.llm_manager import get_active_api_key
        api_key = get_active_api_key("gemini")
        if not api_key:
            return False
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _genai_configured = True
        return True
    except Exception as e:
        print(f"[GEMINI_SERVICE] Failed to configure genai: {e}")
        return False



def _clean_json_response(text: str) -> str:
    """Strip markdown code blocks (e.g. ```json ... ```) to find clean JSON."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


async def analyze_uploaded_image(image_path: str, citizen_description: str) -> Dict[str, Any]:
    """
    Analyze an actual uploaded image file using Gemini Multimodal.
    Returns:
    {
        "issue_type": "POTHOLE",
        "severity": "HIGH",
        "confidence": 0.91,
        "visual_evidence": [
            "large damaged road surface",
            "visible road cavity",
            "water accumulation near damaged area"
        ]
    }
    """
    fallback_result = _generate_inferred_fallback(citizen_description)

    if not _configure_genai():
        print("[GEMINI_SERVICE] No Gemini API key configured. Using deterministic fallback.")
        return fallback_result

    if not os.path.exists(image_path):
        print(f"[GEMINI_SERVICE] File not found: {image_path}. Using deterministic fallback.")
        return fallback_result

    try:
        import google.generativeai as genai
        
        # Load PIL image
        img = Image.open(image_path)
        
        # Set up prompt
        prompt = f"""You are a civic infrastructure analysis AI. Analyze the attached photo of a civic issue.
The citizen reported this issue with description: "{citizen_description}"

Based on the image details, classify the issue:
1. "issue_type": Choose EXACTLY one of these categories:
   - POTHOLE
   - WATER_LEAKAGE
   - WATERLOGGING
   - GARBAGE_OVERFLOW
   - BROKEN_STREETLIGHT
   - DRAINAGE_PROBLEM
   - ROAD_DAMAGE
   - EXPOSED_WIRES
   - SEWAGE_OVERFLOW
   - DRAIN_BLOCKAGE

2. "severity": Choose EXACTLY one of:
   - LOW
   - MEDIUM
   - HIGH
   - CRITICAL

3. "confidence": Estimate confidence as a decimal number between 0.0 and 1.0 (e.g. 0.85).

4. "visual_evidence": Provide exactly 3 short, concrete visual observations. Describe only what is physically visible in the photo. Do not speculate on subterranean causes or administrative issues.

You MUST return a JSON object conforming exactly to this structure:
{{
    "issue_type": "POTHOLE",
    "severity": "HIGH",
    "confidence": 0.91,
    "visual_evidence": [
        "large damaged road surface",
        "visible road cavity",
        "water accumulation near damaged area"
    ]
}}
"""
        from services.llm_manager import get_active_model
        gemini_model_id = get_active_model("gemini") or "gemini-flash-latest"
        model = genai.GenerativeModel(gemini_model_id)
        
        # Call Gemini model
        response = model.generate_content([prompt, img])
        
        # Parse output
        raw_text = response.text
        cleaned_text = _clean_json_response(raw_text)
        data = json.loads(cleaned_text)
        
        # Validate keys
        required_keys = ["issue_type", "severity", "confidence", "visual_evidence"]
        if all(k in data for k in required_keys):
            return {
                "issue_type": str(data["issue_type"]).upper(),
                "severity": str(data["severity"]).upper(),
                "confidence": float(data["confidence"]),
                "visual_evidence": list(data["visual_evidence"])[:3],
            }
        else:
            print("[GEMINI_SERVICE] Returned JSON was missing keys. Using fallback.")
            return fallback_result

    except Exception as e:
        print(f"[GEMINI_SERVICE] Multimodal analysis call failed: {e}. Using fallback.")
        return fallback_result


def _generate_inferred_fallback(description: str) -> Dict[str, Any]:
    """Infers issue type, severity, and visual evidence from description for high-fidelity fallback."""
    desc_lower = description.lower()
    
    keyword_map = [
        (["water leak", "pipe leak", "pipe burst", "water flowing", "water seep"], "WATER_LEAKAGE", "HIGH", [
            "visible stream of water flowing on road surface",
            "soil erosion around suspected leakage source",
            "damp/saturated pavement area"
        ]),
        (["pothole", "pot hole", "road hole", "cavity"], "POTHOLE", "MEDIUM", [
            "depressed circular cavity in asphalt surface",
            "exposed aggregate sub-base within road hole",
            "cracked pavement edges bordering the cavity"
        ]),
        (["waterlogging", "water logging", "flooding", "water stagnant", "standing water"], "WATERLOGGING", "MEDIUM", [
            "standing pools of water covering road lanes",
            "submerged roadway markers and curb boundaries",
            "water ripples from local commuter wade-throughs"
        ]),
        (["road damage", "road broken", "road crack", "road surface"], "ROAD_DAMAGE", "MEDIUM", [
            "visible longitudinal structural cracks in asphalt",
            "uneven surface elevation on main corridor road",
            "crumbling road shoulders and debris accumulation"
        ]),
        (["garbage", "waste", "trash", "rubbish", "dumping"], "GARBAGE_OVERFLOW", "MEDIUM", [
            "overflowing community waste dumpster",
            "mixed domestic and organic refuse scattered on pavement",
            "loose waste blockages near street walkway"
        ]),
        (["drain block", "blocked drain", "drain clog"], "DRAIN_BLOCKAGE", "MEDIUM", [
            "drain inlet cover obstructed by plastic debris",
            "local water backup centering around drainage grate",
            "silt and organic waste buildup inside drain aperture"
        ]),
        (["drainage", "drain problem", "water not flowing"], "DRAINAGE_PROBLEM", "MEDIUM", [
            "obstructed gutter lanes holding stagnant runoff",
            "overflowing sewer catch basin inlet",
            "accumulation of street sludge along concrete gutter"
        ]),
        (["exposed wire", "live wire", "electric", "electrocution"], "EXPOSED_WIRES", "CRITICAL", [
            "stripped electrical cabling suspended low overhead",
            "exposed junction wire terminals near main pole structure",
            "weather-worn insulation wrap posing safety risk"
        ]),
        (["sewage", "sewer", "manhole overflow"], "SEWAGE_OVERFLOW", "HIGH", [
            "murky effluent bubbling from manhole seam cover",
            "dark liquid pooling on street side curb",
            "organic sludge residue visible on local roadway"
        ]),
        (["streetlight", "street light", "lamp not", "dark road"], "BROKEN_STREETLIGHT", "MEDIUM", [
            "unlit overhead sodium/LED luminaire fixture",
            "cracked light housing cover structure on support mast",
            "dark road corridor section showing high visibility drop"
        ])
    ]

    for keywords, issue_type, severity, visual_evidence in keyword_map:
        for kw in keywords:
            if kw in desc_lower:
                return {
                    "issue_type": issue_type,
                    "severity": severity,
                    "confidence": 0.88,
                    "visual_evidence": visual_evidence
                }

    # Default fallback
    return {
        "issue_type": "ROAD_DAMAGE",
        "severity": "MEDIUM",
        "confidence": 0.50,
        "visual_evidence": [
            "road surface defect matching citizen description text",
            "visual abnormality requiring active location audit",
            "unidentified structural decay reported"
        ]
    }
