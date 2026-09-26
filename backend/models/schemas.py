"""
OmniCivic AI — Shared State Schema
Every agent reads/writes a single shared IncidentContext object.
This is what makes them a pipeline instead of disconnected scripts.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


# ─── Enums ──────────────────────────────────────────────────────────────────────

class IncidentStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ASSIGNED = "ASSIGNED"
    ACTION_IN_PROGRESS = "ACTION_IN_PROGRESS"
    AWAITING_RESOLUTION_EVIDENCE = "AWAITING_RESOLUTION_EVIDENCE"
    RESOLUTION_REVIEW = "RESOLUTION_REVIEW"
    RESOLVED = "RESOLVED"
    REOPENED = "REOPENED"
    ESCALATED = "ESCALATED"


class IssueType(str, Enum):
    POTHOLE = "POTHOLE"
    WATER_LEAKAGE = "WATER_LEAKAGE"
    WATERLOGGING = "WATERLOGGING"
    GARBAGE_OVERFLOW = "GARBAGE_OVERFLOW"
    BROKEN_STREETLIGHT = "BROKEN_STREETLIGHT"
    DRAINAGE_PROBLEM = "DRAINAGE_PROBLEM"
    ROAD_DAMAGE = "ROAD_DAMAGE"
    EXPOSED_WIRES = "EXPOSED_WIRES"
    SEWAGE_OVERFLOW = "SEWAGE_OVERFLOW"
    DRAIN_BLOCKAGE = "DRAIN_BLOCKAGE"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReportStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    LINKED_TO_INCIDENT = "LINKED_TO_INCIDENT"
    RESOLVED = "RESOLVED"


class VerificationResult(str, Enum):
    RESOLUTION_VERIFIED = "RESOLUTION_VERIFIED"
    LOCATION_MISMATCH = "LOCATION_MISMATCH"
    POSSIBLE_FAILED_RESOLUTION = "POSSIBLE_FAILED_RESOLUTION"
    PENDING = "PENDING"


class IncidentClassification(str, Enum):
    INDEPENDENT_COMPLAINTS = "INDEPENDENT_COMPLAINTS"
    DUPLICATE_REPORTS = "DUPLICATE_REPORTS"
    POSSIBLE_CONNECTED_INCIDENT = "POSSIBLE_CONNECTED_INCIDENT"
    HIGH_CONFIDENCE_CONNECTED_INCIDENT = "HIGH_CONFIDENCE_CONNECTED_INCIDENT"


# ─── Sub-models ─────────────────────────────────────────────────────────────────

class Location(BaseModel):
    latitude: float
    longitude: float
    address: str = ""
    ward: str = ""


class CivicReport(BaseModel):
    """A single citizen complaint/report."""
    report_id: str
    timestamp: str
    citizen_name: str = "Anonymous"
    phone: str = ""
    location: Location
    description: str
    image_filename: str = ""
    status: str = ReportStatus.SUBMITTED
    linked_incident_id: Optional[str] = None
    ward: str = ""
    scenario_id: Optional[int] = None  # For demo tracking


class PerceptionResult(BaseModel):
    """Output of the Perception Agent for a single report."""
    report_id: str
    issue_type: str
    severity: str
    confidence: float
    evidence_text: str = ""
    image_filename: str = ""
    visual_evidence: List[str] = Field(default_factory=list)


class ClusterInfo(BaseModel):
    """Cluster metadata from the Geo-Temporal Clustering Agent."""
    radius_m: float = 0.0
    time_window_days: int = 0
    center_lat: float = 0.0
    center_lon: float = 0.0
    report_count: int = 0


class RootCause(BaseModel):
    """Output of the Root Cause Investigation Agent."""
    hypothesis: str = ""
    confidence: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    chain: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "AI-generated civic incident hypothesis. "
        "Physical inspection recommended."
    )
    tools_used: List[str] = Field(default_factory=list)
    reasoning_notes: str = ""
    nearby_sites: List[dict] = Field(default_factory=list)




class ImpactBreakdown(BaseModel):
    """Detailed breakdown of the impact score components."""
    severity_score: float = 0.0
    infrastructure_proximity: float = 0.0
    people_affected: float = 0.0
    duration: float = 0.0
    repeat_reports: float = 0.0
    secondary_risk: float = 0.0


class ImpactScore(BaseModel):
    """Output of the Civic Impact Agent."""
    score: float = 0.0
    priority: str = Priority.LOW
    breakdown: ImpactBreakdown = Field(default_factory=ImpactBreakdown)
    explanation: str = ""


class ResponseStep(BaseModel):
    """A single step in a multi-department response plan."""
    step_number: int
    department: str
    department_name: str = ""
    action: str
    reason: str = ""
    estimated_hours: int = 0
    depends_on: List[int] = Field(default_factory=list)


class ResponsePlan(BaseModel):
    """Output of the Response Orchestration Agent."""
    steps: List[ResponseStep] = Field(default_factory=list)
    rationale: str = ""
    approved: bool = False
    approved_by: str = ""
    approved_at: str = ""


class Resolution(BaseModel):
    """Resolution evidence and verification result."""
    before_photo: str = ""
    after_photo: str = ""
    before_gps: Optional[Location] = None
    after_gps: Optional[Location] = None
    submitted_at: str = ""
    verification_result: str = VerificationResult.PENDING
    verification_details: str = ""
    confidence: float = 0.0
    verified_by_agent: bool = False


class SLA(BaseModel):
    """SLA tracking for an incident."""
    deadline: str = ""
    reminders_sent: int = 0
    escalated: bool = False
    escalation_reason: str = ""
    original_deadline: str = ""


class AgentLogEntry(BaseModel):
    """
    A single agent log entry.
    Every AI decision displays: DECISION → EVIDENCE USED → CONFIDENCE → RECOMMENDED ACTION.
    """
    timestamp: str
    agent: str
    message: str
    decision: str = ""
    evidence_used: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    recommended_action: str = ""


# ─── Core shared state ──────────────────────────────────────────────────────────

class IncidentContext(BaseModel):
    """
    The single shared state object that every agent reads and writes.
    The Orchestrator is the sole writer to disk.
    """
    incident_id: str
    status: str = IncidentStatus.SUBMITTED
    classification: str = IncidentClassification.INDEPENDENT_COMPLAINTS
    reasoning_mode: str = "deterministic_fallback"
    created_at: str = ""
    updated_at: str = ""
    connected_reports: List[str] = Field(default_factory=list)
    cluster: ClusterInfo = Field(default_factory=ClusterInfo)
    perception_results: List[PerceptionResult] = Field(default_factory=list)
    root_cause: RootCause = Field(default_factory=RootCause)
    impact_score: ImpactScore = Field(default_factory=ImpactScore)
    response_plan: ResponsePlan = Field(default_factory=ResponsePlan)
    resolution: Resolution = Field(default_factory=Resolution)
    sla: SLA = Field(default_factory=SLA)
    agent_log: List[AgentLogEntry] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    tool_traces: List[dict] = Field(default_factory=list)
    nearby_sites: List[dict] = Field(default_factory=list)
    scenario_id: Optional[int] = None  # For demo tracking




# ─── API request/response models ────────────────────────────────────────────────

class SubmitReportRequest(BaseModel):
    citizen_name: str = "Anonymous"
    phone: str = ""
    latitude: float
    longitude: float
    address: str = ""
    ward: str = ""
    description: str
    image_filename: str = ""


class SubmitReportResponse(BaseModel):
    report_id: str
    status: str
    message: str
    timestamp: str


class AnalyzeReportResponse(BaseModel):
    report_id: str
    perception: PerceptionResult
    cluster_size: int
    nearby_report_ids: List[str] = Field(default_factory=list)
    incident_id: Optional[str] = None
    incident_classification: Optional[str] = None


class ResolutionSubmission(BaseModel):
    after_photo: str
    after_latitude: float
    after_longitude: float
    notes: str = ""


class DashboardStats(BaseModel):
    total_reports: int = 0
    total_incidents: int = 0
    active_incidents: int = 0
    critical_incidents: int = 0
    resolved_incidents: int = 0
    reopened_incidents: int = 0
    escalated_incidents: int = 0


class ScenarioInfo(BaseModel):
    scenario_id: int
    title: str
    description: str
    report_ids: List[str] = Field(default_factory=list)
    incident_id: Optional[str] = None
