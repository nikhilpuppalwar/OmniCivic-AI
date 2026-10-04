"""
OmniCivic AI -- FastAPI Backend
Autonomous Civic Incident Intelligence System

"Different complaints. One hidden signal."
"""

import json
import os
import shutil
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── Paths ────────────────────────────────────────────────────────────────────

import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")
SEED_IMAGES_DIR = os.path.join(BASE_DIR, "seed_images")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(SEED_IMAGES_DIR, exist_ok=True)

ENABLE_DEV_ENDPOINTS = os.getenv("ENABLE_DEV_ENDPOINTS", "true").lower() in ("true", "1", "yes")


def require_dev_endpoints():
    if not ENABLE_DEV_ENDPOINTS:
        raise HTTPException(
            status_code=403,
            detail="Development endpoints are disabled in this environment (ENABLE_DEV_ENDPOINTS=false)."
        )

# ── IST timezone helper ─────────────────────────────────────────────────────

IST = timezone(timedelta(hours=5, minutes=30))


def now_ist() -> str:
    return datetime.now(IST).isoformat()


# ── JSON data helpers ────────────────────────────────────────────────────────

def load_json(filename: str) -> dict:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename: str, data: dict):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_complaints() -> dict:
    return load_json("complaints.json")


def save_complaints(data: dict):
    save_json("complaints.json", data)


def load_incidents() -> dict:
    return load_json("incidents.json")


def save_incidents(data: dict):
    save_json("incidents.json", data)


def load_agent_logs() -> dict:
    return load_json("agent_logs.json")


def save_agent_logs(data: dict):
    save_json("agent_logs.json", data)


def append_agent_log(entry: dict):
    logs = load_agent_logs()
    if "logs" not in logs:
        logs["logs"] = []
    logs["logs"].append(entry)
    logs["total"] = len(logs["logs"])
    save_agent_logs(logs)


def load_perception_lookup() -> dict:
    return load_json("perception_lookup.json")


def load_scenarios() -> dict:
    return load_json("scenarios.json")


def load_departments() -> dict:
    return load_json("departments.json")


def load_dependencies() -> dict:
    return load_json("civic_dependencies.json")


def next_report_id() -> str:
    data = load_complaints()
    reports = data.get("reports", [])
    if not reports:
        return "CIV-2026-1051"
    max_num = 0
    for r in reports:
        try:
            num = int(r["report_id"].split("-")[-1])
            if num > max_num:
                max_num = num
        except (ValueError, IndexError):
            pass
    return f"CIV-2026-{max_num + 1}"


def next_incident_id() -> str:
    data = load_incidents()
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


# ── FastAPI app ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="OmniCivic AI",
    description="Autonomous Civic Incident Intelligence System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve seed images with extension fallback (.jpg -> .png)
from fastapi.responses import FileResponse

@app.get("/seed-images/{filename}")
async def serve_seed_image(filename: str):
    """Serve a seed image, trying .png fallback if .jpg not found."""
    path = os.path.join(SEED_IMAGES_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path)
    # Try alternate extension
    base, ext = os.path.splitext(filename)
    if ext.lower() == ".jpg":
        alt_path = os.path.join(SEED_IMAGES_DIR, base + ".png")
        if os.path.exists(alt_path):
            return FileResponse(alt_path)
    elif ext.lower() == ".png":
        alt_path = os.path.join(SEED_IMAGES_DIR, base + ".jpg")
        if os.path.exists(alt_path):
            return FileResponse(alt_path)
    raise HTTPException(status_code=404, detail=f"Image {filename} not found")

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


# ── Request/Response models ─────────────────────────────────────────────────

class SubmitReportRequest(BaseModel):
    citizen_name: str = "Anonymous"
    phone: str = ""
    latitude: float
    longitude: float
    address: str = ""
    ward: str = ""
    description: str
    image_filename: str = ""


class ResolutionSubmission(BaseModel):
    after_photo: str
    after_latitude: float
    after_longitude: float
    notes: str = ""


class AdvanceDemoTimeRequest(BaseModel):
    hours: int = 72  # Default: 3 days


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES: Reports
# ══════════════════════════════════════════════════════════════════════════════

# Ensure uploads directory for reports exists
REPORTS_UPLOADS_DIR = os.path.join(UPLOADS_DIR, "reports")
os.makedirs(REPORTS_UPLOADS_DIR, exist_ok=True)

@app.post("/reports")
async def submit_report(
    image: Optional[UploadFile] = File(None),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_name: str = Form(""),
    citizen_name: str = Form("Anonymous"),
    phone: str = Form(""),
    ward: str = Form(""),
    image_filename: Optional[str] = Form(None),
):
    """Submit a new civic complaint report (handles upload or demo image)."""
    saved_filename = ""
    
    if image is not None and image.filename:
        # Validate MIME type
        content_type = image.content_type
        if content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Only JPG, PNG, and WEBP are allowed."
            )
        
        # Determine extension
        ext = ".jpg"
        if content_type == "image/png":
            ext = ".png"
        elif content_type == "image/webp":
            ext = ".webp"
            
        # Generate UUID filename
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        saved_filename = f"report_{unique_id}{ext}"
        
        # Save image
        file_path = os.path.join(REPORTS_UPLOADS_DIR, saved_filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save uploaded image: {e}")
    else:
        # Check if demo image is provided
        if not image_filename:
            raise HTTPException(
                status_code=400,
                detail="Either an image upload or a demo image selection is required."
            )
        saved_filename = image_filename

    report_id = next_report_id()
    final_address = location_name if location_name else "Unknown Location"

    report = {
        "report_id": report_id,
        "timestamp": now_ist(),
        "citizen_name": citizen_name,
        "phone": phone,
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "address": final_address,
            "ward": ward,
        },
        "description": description,
        "image_filename": saved_filename,
        "status": "SUBMITTED",
        "linked_incident_id": None,
        "ward": ward,
        "scenario_id": None,
    }

    data = load_complaints()
    data["reports"].append(report)
    data["total"] = len(data["reports"])
    save_complaints(data)

    return {
        "report_id": report_id,
        "status": "SUBMITTED",
        "message": f"Report {report_id} submitted successfully.",
        "timestamp": report["timestamp"],
    }


@app.get("/reports")
async def list_reports(ward: Optional[str] = None, status: Optional[str] = None):
    """List all reports, optionally filtered by ward or status."""
    data = load_complaints()
    reports = data.get("reports", [])

    if ward:
        reports = [r for r in reports if r.get("ward", "") == ward]
    if status:
        reports = [r for r in reports if r.get("status", "") == status]

    return {"reports": reports, "total": len(reports)}


@app.get("/reports/{report_id}")
async def get_report(report_id: str):
    """Get a single report by ID."""
    data = load_complaints()
    for r in data.get("reports", []):
        if r["report_id"] == report_id:
            return r
    raise HTTPException(status_code=404, detail=f"Report {report_id} not found")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES: Analysis (Perception + Clustering + Incident Detection)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/analyze/{report_id}")
async def analyze_report(report_id: str):
    """
    Run the full agent pipeline on a report:
    Perception -> Clustering -> Incident Detection -> Root Cause -> Impact -> Response
    """
    # Import agents here to avoid circular imports at startup
    from agents.orchestrator import run_full_pipeline

    data = load_complaints()
    report = None
    for r in data.get("reports", []):
        if r["report_id"] == report_id:
            report = r
            break

    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    # Run the full agent pipeline
    result = await run_full_pipeline(report)
    return result


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES: Incidents
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/incidents")
async def list_incidents():
    """List all incidents."""
    data = load_incidents()
    return data


@app.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get a single incident by ID."""
    data = load_incidents()
    for inc in data.get("incidents", []):
        if inc["incident_id"] == incident_id:
            return inc
    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")


@app.post("/incidents/{incident_id}/analyze")
async def analyze_incident(incident_id: str):
    """Re-run analysis on an existing incident."""
    from agents.orchestrator import analyze_existing_incident

    data = load_incidents()
    incident = None
    for inc in data.get("incidents", []):
        if inc["incident_id"] == incident_id:
            incident = inc
            break

    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    result = await analyze_existing_incident(incident)
    return result


@app.get("/incidents/{incident_id}/impact")
async def get_incident_impact(incident_id: str):
    """Get impact score for an incident."""
    data = load_incidents()
    for inc in data.get("incidents", []):
        if inc["incident_id"] == incident_id:
            return inc.get("impact_score", {})
    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")


@app.get("/incidents/{incident_id}/response-plan")
async def get_response_plan(incident_id: str):
    """Get response plan for an incident."""
    data = load_incidents()
    for inc in data.get("incidents", []):
        if inc["incident_id"] == incident_id:
            return inc.get("response_plan", {})
    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")


@app.post("/incidents/{incident_id}/approve-plan")
async def approve_response_plan(incident_id: str):
    """Human-in-the-loop: Approve a response plan."""
    data = load_incidents()
    for inc in data.get("incidents", []):
        if inc["incident_id"] == incident_id:
            if not inc.get("response_plan", {}).get("steps"):
                raise HTTPException(status_code=400, detail="No response plan to approve")

            inc["response_plan"]["approved"] = True
            inc["response_plan"]["approved_by"] = "Authority Officer"
            inc["response_plan"]["approved_at"] = now_ist()
            inc["status"] = "ACTION_IN_PROGRESS"
            inc["updated_at"] = now_ist()

            # Log the approval
            append_agent_log({
                "timestamp": now_ist(),
                "agent": "HUMAN_AUTHORITY",
                "message": f"Response plan for {incident_id} approved by authority officer.",
                "decision": "PLAN_APPROVED",
                "evidence_used": ["Human review of multi-department response plan"],
                "confidence": 1.0,
                "recommended_action": "Proceed with plan execution",
            })

            save_incidents(data)
            return {
                "incident_id": incident_id,
                "status": "ACTION_IN_PROGRESS",
                "message": "Response plan approved. Departments notified.",
                "approved_at": inc["response_plan"]["approved_at"],
            }

    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES: Resolution
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/incidents/{incident_id}/resolution")
async def submit_resolution(incident_id: str, req: ResolutionSubmission):
    """Submit resolution evidence (after photo + GPS)."""
    data = load_incidents()
    for inc in data.get("incidents", []):
        if inc["incident_id"] == incident_id:
            inc["resolution"] = {
                "before_photo": inc.get("resolution", {}).get("before_photo", ""),
                "after_photo": req.after_photo,
                "before_gps": None,
                "after_gps": {
                    "latitude": req.after_latitude,
                    "longitude": req.after_longitude,
                },
                "submitted_at": now_ist(),
                "verification_result": "PENDING",
                "verification_details": "",
                "confidence": 0.0,
                "verified_by_agent": False,
            }
            inc["status"] = "RESOLUTION_REVIEW"
            inc["updated_at"] = now_ist()
            save_incidents(data)

            return {
                "incident_id": incident_id,
                "status": "RESOLUTION_REVIEW",
                "message": "Resolution evidence submitted. Awaiting verification.",
            }

    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")


@app.post("/incidents/{incident_id}/verify-resolution")
async def verify_resolution(incident_id: str):
    """Run the Resolution Verification Agent on submitted evidence."""
    from agents.verification import verify_resolution as run_verification

    data = load_incidents()
    for inc in data.get("incidents", []):
        if inc["incident_id"] == incident_id:
            if not inc.get("resolution", {}).get("after_photo"):
                raise HTTPException(
                    status_code=400,
                    detail="No resolution evidence submitted yet",
                )

            result = await run_verification(inc)

            # Update incident with verification result
            inc["resolution"]["verification_result"] = result["verification_result"]
            inc["resolution"]["verification_details"] = result["verification_details"]
            inc["resolution"]["confidence"] = result["confidence"]
            inc["resolution"]["verified_by_agent"] = True

            if result["verification_result"] == "RESOLUTION_VERIFIED":
                inc["status"] = "RESOLVED"
                inc["impact_score"]["priority"] = "LOW"
            elif result["verification_result"] == "LOCATION_MISMATCH":
                inc["status"] = "AWAITING_RESOLUTION_EVIDENCE"
            elif result["verification_result"] == "POSSIBLE_FAILED_RESOLUTION":
                inc["status"] = "REOPENED"

            inc["updated_at"] = now_ist()
            save_incidents(data)
            return result

    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES: Escalation & Demo
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/incidents/{incident_id}/advance-demo-time")
async def advance_demo_time(incident_id: str, req: AdvanceDemoTimeRequest):
    """Advance demo time to trigger escalation."""
    from agents.escalation import check_escalation

    data = load_incidents()
    for inc in data.get("incidents", []):
        if inc["incident_id"] == incident_id:
            result = await check_escalation(inc, advance_hours=req.hours)

            # Update the incident
            inc["status"] = result["new_status"]
            inc["sla"] = result["sla"]
            inc["updated_at"] = now_ist()
            save_incidents(data)

            return result

    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES: Agent Logs & Dashboard
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/agent-logs")
async def get_agent_logs(incident_id: Optional[str] = None, agent: Optional[str] = None):
    """Get agent execution logs, optionally filtered."""
    data = load_agent_logs()
    logs = data.get("logs", [])

    if incident_id:
        logs = [l for l in logs if incident_id in l.get("message", "")]
    if agent:
        logs = [l for l in logs if l.get("agent", "") == agent]

    return {"logs": logs, "total": len(logs)}


@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics."""
    complaints = load_complaints()
    incidents_data = load_incidents()

    reports = complaints.get("reports", [])
    incidents = incidents_data.get("incidents", [])

    active_statuses = {"SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "ACTION_IN_PROGRESS",
                       "AWAITING_RESOLUTION_EVIDENCE", "RESOLUTION_REVIEW"}
    active = [i for i in incidents if i.get("status") in active_statuses]
    critical = [i for i in incidents if i.get("impact_score", {}).get("priority") == "CRITICAL"]
    resolved = [i for i in incidents if i.get("status") == "RESOLVED"]
    reopened = [i for i in incidents if i.get("status") == "REOPENED"]
    escalated = [i for i in incidents if i.get("status") == "ESCALATED"]

    return {
        "total_reports": len(reports),
        "total_incidents": len(incidents),
        "active_incidents": len(active),
        "critical_incidents": len(critical),
        "resolved_incidents": len(resolved),
        "reopened_incidents": len(reopened),
        "escalated_incidents": len(escalated),
    }


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES: Dev/Demo tools
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/dev/reset-demo")
async def reset_demo():
    """Reset all data to pre-demo state."""
    require_dev_endpoints()
    from scripts.seed_data import generate_seed_data
    generate_seed_data()
    return {"message": "Demo data reset successfully.", "timestamp": now_ist()}


@app.get("/dev/scenarios")
async def get_scenarios():
    """Get demo scenario metadata."""
    return load_scenarios()


@app.get("/dev/seed-images")
async def list_seed_images():
    """List available seed images for the demo."""
    if not os.path.exists(SEED_IMAGES_DIR):
        return {"images": []}
    images = [f for f in os.listdir(SEED_IMAGES_DIR)
              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    return {"images": sorted(images)}


@app.get("/dev/perception-lookup")
async def get_perception_lookup():
    """Get the perception lookup table (for demo transparency)."""
    return load_perception_lookup()


@app.get("/geocode")
@app.get("/api/geocode")
async def geocode_query(q: str = ""):
    """Free geocoding proxy using OpenStreetMap Nominatim with rate-limiting, caching, and offline fallback."""
    from services.external_tools import geocode_address
    results = await geocode_address(q)
    return {"query": q, "results": results, "count": len(results)}


# ══════════════════════════════════════════════════════════════════════════════
# Health check
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# ROUTES: LLM Provider & Key Configuration (Operator Authenticated)
# ══════════════════════════════════════════════════════════════════════════════

from services.llm_manager import (
    get_operator_token,
    validate_operator_token,
    get_public_settings_payload,
    save_provider_config,
    set_active_provider,
    delete_provider_config,
    test_llm_connection,
)

# Trigger operator access token banner in terminal on server boot
try:
    get_operator_token()
except Exception as _e:
    pass


def verify_operator_token(x_operator_token: Optional[str] = Header(None, alias="X-Operator-Token")) -> str:
    """Authorize requests to /api/settings using X-Operator-Token header."""
    if not validate_operator_token(x_operator_token):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Missing or invalid X-Operator-Token header. Check server terminal output or backend/.operator_token."
        )
    return x_operator_token or ""


class ProviderConfigRequest(BaseModel):
    provider_id: Optional[str] = None
    provider: Optional[str] = None  # backward-compat
    api_key: Optional[str] = ""
    model: Optional[str] = ""
    base_url: Optional[str] = ""
    temperature: Optional[float] = 0.3
    set_active: Optional[bool] = False


class SetActiveProviderRequest(BaseModel):
    provider_id: str


class LLMTestRequest(BaseModel):
    provider: str
    api_key: Optional[str] = ""
    model: Optional[str] = ""
    base_url: Optional[str] = ""


@app.get("/api/settings/dev-token")
async def get_dev_token():
    """Development helper: returns the active local operator access token for 1-click UI authorization."""
    require_dev_endpoints()
    return {"token": get_operator_token()}


@app.get("/api/settings")
async def get_settings(_token: str = Depends(verify_operator_token)):
    """Retrieve multi-provider configurations and active provider indicator."""
    return get_public_settings_payload()


@app.post("/api/settings")
async def update_settings(req: ProviderConfigRequest, _token: str = Depends(verify_operator_token)):
    """Save or update a provider config with masked-value overwrite protection and empty-field clearing."""
    pid = (req.provider_id or req.provider or "mock").lower().strip()
    payload = await save_provider_config(
        provider_id=pid,
        api_key=req.api_key or "",
        model=req.model or "",
        temperature=req.temperature if req.temperature is not None else 0.3,
        base_url=req.base_url or "",
        set_active=bool(req.set_active),
    )
    return {"message": f"Configuration for provider '{pid}' saved successfully.", "settings": payload}


@app.post("/api/settings/set-active")
async def set_active(req: SetActiveProviderRequest, _token: str = Depends(verify_operator_token)):
    """Switch active LLM provider without altering stored credentials."""
    pid = req.provider_id.lower().strip()
    payload = await set_active_provider(pid)
    return {"message": f"Active LLM provider set to '{pid}'.", "settings": payload}


@app.delete("/api/settings/provider/{provider_id}")
async def delete_provider(provider_id: str, _token: str = Depends(verify_operator_token)):
    """Remove stored credentials for a provider. Rejects mock; auto-resets active provider to mock if active."""
    try:
        payload = await delete_provider_config(provider_id)
        return {"message": f"Provider '{provider_id}' deleted successfully.", "settings": payload}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Failed to delete provider '{provider_id}': {str(ex)}")


@app.post("/api/settings/test")
async def test_settings(req: LLMTestRequest, _token: str = Depends(verify_operator_token)):
    """Lightweight 10s ping diagnostic test. Leaves active_provider unchanged."""
    result = await test_llm_connection(
        provider=req.provider,
        api_key=req.api_key or "",
        model=req.model or "",
        base_url=req.base_url or "",
    )
    return result


@app.get("/")
async def root():

    return {
        "name": "OmniCivic AI",
        "tagline": "Different complaints. One hidden signal.",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": now_ist()}
