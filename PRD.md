# OmniCivic AI — Product Requirements Document (PRD)

> **Tagline:** *"Different complaints. One hidden signal."*  
> **Framing Line:** *"Cities don't have a shortage of complaints. They have a shortage of intelligence connecting those complaints."*

---

## 1. Product Executive Summary

**OmniCivic AI** is an autonomous multi-agent civic incident intelligence system designed for municipal operators, ward officers, and citizens. Municipalities currently process thousands of isolated citizen complaint tickets daily. Traditional systems treat each ticket independently, leading to superficial symptoms being repaired (e.g., patching a pothole) while the underlying root cause (e.g., a leaking water main weakening the road sub-base) remains unaddressed.

OmniCivic AI correlates geographical and temporal proximity across independent citizen reports, identifies cascading root-cause infrastructure failures, automatically assigns multi-department resolution plans in sequenced order, and validates resolution outcomes via automated GPS and photographic verification.

---

## 2. Core Problem Statement

1. **Ticket Fragmentation:** Citizens report symptoms (e.g., waterlogging, potholes, garbage accumulation) independently without knowing they stem from a shared infrastructure failure.
2. **Symptom-Only Remediation:** Municipal departments act in isolation. Road departments fix road surfaces before water supply departments repair leaking pipes, resulting in immediate re-destruction of new road surfaces.
3. **Complaint Volume vs Risk Misalignment:** High complaint counts on minor issues consume municipal resources, while critical low-volume safety threats (e.g., 2 reports of exposed live wires near a school) are deprioritized.
4. **Fraudulent / Inadequate Resolution Closing:** Contractors or field teams report issues as "Resolved" without verifiable physical proof or location alignment.

---

## 3. User Personas

### Persona A: Municipal Authority Operator (Primary User)
- **Role:** Ward Administrator / City Infrastructure Controller.
- **Goals:** Gain a real-time, unified overview of city incidents; identify root causes before dispatching crews; track multi-department execution; prevent SLA breaches.
- **Needs:** Intelligent root-cause alerts, prioritized threat scores, automated workflow sequencing, transparent AI logs.

### Persona B: Field Officer / Department Lead
- **Role:** Water Supply, Drainage, or Roads Department Supervisor.
- **Goals:** Receive clear, actionable work orders; understand dependency sequence (e.g., wait until Water Board finishes before paving).
- **Needs:** Traceable municipal filing codes, precise location coordinates, photo proof requirements.

### Persona C: Concerned Citizen (Secondary User)
- **Role:** Resident reporting local infrastructure breakdown.
- **Goals:** Easily submit report with photo + GPS location; track resolution state; ensure reported issue receives proper attention.
- **Needs:** Frictionless submission UI, visual progress indicators, transparent status updates.

---

## 4. Product Objectives & Key Results (OKRs)

- **Objective 1:** Shift municipal operations from reactive ticket handling to proactive root-cause intelligence.
  - *KR 1.1:* Group 90%+ of geographically and temporally co-located complaints into unified incident clusters within 5 seconds of analysis.
  - *KR 1.2:* Correctly detect multi-stage causal chains (e.g., Water Leak → Road Damage → Pothole → Waterlogging).
- **Objective 2:** Prevent wasteful department execution loops.
  - *KR 2.1:* Enforce 100% topological sequence ordering in multi-department response plans (e.g., Root Cause fixes before surface repairs).
- **Objective 3:** Eliminate false resolution closures.
  - *KR 3.1:* Enforce automated dual-check (GPS distance threshold <100m + visual context matching) on resolution verification evidence.

---

## 5. Functional Requirements

### FR-1: Citizen Complaint Submission
- Allow citizens to submit reports with description, ward, location coordinates, and photo evidence.
- Support both live image uploads and pre-seeded demo complaint images.

### FR-2: Autonomous Multi-Agent Analysis Pipeline
- Provide a single-click **Run Agentic AI** trigger to execute 7 coordinated analysis stages:
  1. *Perception:* Detect issue category, severity, and visual evidence.
  2. *Clustering:* Group complaints within 180m and 7-day windows.
  3. *Incident Detection:* Classify cluster relationships (Independent, Duplicate, Connected).
  4. *Root-Cause Graph Analysis:* Trace causal cascades using dependency graph math and LLM evidence synthesis.
  5. *Civic Impact Scoring:* Calculate 0-100 threat score based on multi-factor weighted math.
  6. *Response Planning:* Generate sequenced multi-department execution plan with topological dependency resolution.
  7. *Municipal Filing:* Generate simulated traceable filing code (`FILE-[INC_ID]`).

### FR-3: Interactive Authority Operations Dashboard
- Display global metrics: Total Reports, Active Incidents, Critical Priority, Resolved, Reopened, Escalated SLAs.
- Render interactive citizen report feed and active incident cards.
- Provide interactive execution trace showing agent decisions, confidence levels, and evidence used.

### FR-4: Human-in-the-Loop Approval & Resolution Verification
- Require authority officer approval for multi-department response plans before state transitions to `ACTION_IN_PROGRESS`.
- Support field resolution submission with "After" photo and GPS coordinates.
- Automatically verify resolution evidence:
  - *Pass:* Status becomes `RESOLVED`, impact score drops to `LOW`.
  - *Location Mismatch:* Status set to `AWAITING_RESOLUTION_EVIDENCE`, ticket remains open.
  - *Failed Repair:* Status set to `REOPENED`.

### FR-5: SLA Monitoring & Time-Travel Simulation
- Track SLA deadlines per priority level (Critical: 4-12h, High: 16-48h, Medium: 36-72h, Low: 72-120h).
- Provide a demo **Advance Time (+3 Days)** trigger to simulate SLA expiration and automatic priority escalation to management.

---

## 6. Non-Functional Requirements

- **Performance:** Agent pipeline execution completes in under 3 seconds in deterministic mode.
- **Reliability:** 100% availability during live demos via dual-mode fallback (Anthropic/Gemini live APIs with deterministic offline lookups).
- **Usability:** High-contrast dark mode interface with real-time state feedback and visual progress indicators.
- **Traceability:** Every decision logged with agent timestamp, confidence rating, and evidence sources.

---

## 7. Demo Scenarios & Rehearsal Flow

1. **Scenario 1 (Water Infrastructure Cascade):** Water leakage near Chakala Junction causing road damage, pothole, and waterlogging (`INC-2026-001`).
2. **Scenario 2 (Drainage-Waste Cycle):** Blocked drain in Kurla causing waterlogging and garbage accumulation (`INC-2026-002`).
3. **Scenario 3 (Electrical Safety Hazard):** Exposed live wires near a school (2 reports, Critical 91/100 score proving priority ≠ complaint count).
4. **Scenario 4 (Recurring Pothole Repair Failure):** Re-opened incident following poor-quality repair on Hill Road.
