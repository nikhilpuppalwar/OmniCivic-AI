# OmniCivic AI — Product Requirements Document (PRD)

> **Tagline:** *"Different complaints. One hidden signal."*  
> **Framing Line:** *"Cities don't have a shortage of complaints. They have a shortage of intelligence connecting those complaints."*

---

## 1. Product Executive Summary

**OmniCivic AI** is an autonomous multi-agent civic incident intelligence system engineered for municipal authorities, ward administrators, and citizens. Municipal contact centers and grievance portals process thousands of isolated complaint tickets every day. Traditional CRM and ticketing platforms treat each ticket independently. This siloed approach leads to superficial symptom patching (e.g., repeatedly asphalt-patching a pothole) while the hidden root cause (e.g., an underground water main leak undermining the road base) remains undetected, wasting public funds and exacerbating urban hazards.

OmniCivic AI continuously correlates geographical and temporal proximity across citizen reports, invokes real-time keyless analytical tools (weather forecasts and OpenStreetMap sensitive sites), uncovers cascading infrastructure failures, automatically schedules sequenced multi-department response plans, and verifies physical resolution outcomes using automated GPS and visual anti-fraud checks.

---

## 2. Core Problem Statement

1. **Ticket Fragmentation:** Citizens report surface symptoms (e.g., waterlogging, potholes, garbage overflow) in isolation, unaware that they originate from a single shared infrastructure failure.
2. **Symptom-Only Remediation Loops:** Municipal departments operate without cross-coordination. Road departments resurface roads before water departments fix underground leaks, causing rapid pavement destruction.
3. **Complaint Volume vs Public Threat Misalignment:** Minor complaints with high viral volume deplete field resources, while critical, low-volume hazards (e.g., 2 reports of exposed live wires near a primary school) are deprioritized.
4. **Contractor Fraud & Unverified Ticket Closure:** Contractors mark grievances as "Resolved" without verifiable physical proof or geographical proximity alignment.
5. **Rigid AI Vendor Lock-in:** Municipalities need flexible LLM deployment options ranging from ultra-fast cloud LPUs (Groq) and frontier reasoning models (Claude, OpenAI, Gemini) to fully offline, zero-key deterministic simulations.

---

## 3. User Personas

### Persona A: Municipal Authority Operator (Primary User)
- **Role:** Ward Administrator / City Infrastructure Controller.
- **Goals:** Real-time visibility into urban incidents; detect root causes before dispatching repair crews; prevent re-repair loops; monitor SLA deadlines.
- **Needs:** Intelligent root-cause alerts, prioritized threat scores, automated workflow sequencing, interactive GIS maps, transparent agent decision logs.

### Persona B: Field Officer / Department Lead
- **Role:** Water Supply, Drainage, Roads, or Electrical Department Supervisor.
- **Goals:** Receive clear, actionable work orders with defined prerequisites (e.g., wait until Water Board completes pipe repair before laying asphalt).
- **Needs:** Traceable municipal filing codes, precise coordinates, photo proof requirements, anti-fraud verification feedback.

### Persona C: Concerned Citizen (Secondary User)
- **Role:** Local resident reporting urban breakdowns.
- **Goals:** Submit reports with photos and auto-detected GPS coordinates; track status transparently; ensure hazards are promptly triaged.
- **Needs:** Mobile-friendly UI, live photo upload, map coordinate picker, clear status updates.

---

## 4. Product Objectives & Key Results (OKRs)

- **Objective 1:** Shift municipal operations from reactive ticket handling to proactive root-cause intelligence.
  - *KR 1.1:* Group 90%+ of geographically and temporally co-located complaints ($d \le 180\text{m}$, $\Delta t \le 7\text{d}$) into unified incident clusters in $<2$ seconds.
  - *KR 1.2:* Correctly hypothesize multi-stage causal chains (e.g., Water Leak $\to$ Road Damage $\to$ Pothole $\to$ Waterlogging).
- **Objective 2:** Prevent wasteful department execution loops.
  - *KR 2.1:* Enforce 100% topological sequence ordering in multi-department response plans (utilities before surface paving).
- **Objective 3:** Eliminate false resolution closures.
  - *KR 3.1:* Enforce automated dual-check ($<100\text{m}$ GPS proximity tolerance + visual context verification) on all resolution submissions.
- **Objective 4:** Provide robust, secure multi-model flexibility.
  - *KR 4.1:* Support 8+ LLM providers with Fernet 256-bit encryption at rest and seamless zero-key offline deterministic fallback.

---

## 5. Functional Requirements

### FR-1: Citizen Complaint Submission Portal
- Provide dual submission modes:
  - **Live Photo Upload:** Supports `image/jpeg`, `image/png`, `image/webp` with drag-and-drop, client-side preview, server-side MIME validation, GPS auto-detection, and interactive Leaflet map pin placement.
  - **Preset Demo Scenarios:** One-click pre-calibrated scenario presets (`leak_01.jpg`, `road_damage_01.jpg`, `pothole_01.jpg`, `waterlogging_01.jpg`, `exposed_wire_01.jpg`, `garbage_01.jpg`, `drain_01.jpg`) with preset coordinates and descriptions.
- Auto-generate structured report tracking IDs (`CIV-2026-XXXX`).

### FR-2: Autonomous Multi-Agent Pipeline Execution
- Provide single-click **Run Agentic AI** trigger orchestrating 7 visual pipeline stages:
  1. *Perception:* Detect issue category, severity, and visual features.
  2. *Clustering:* Cluster reports within 180m and 7-day temporal window.
  3. *Incident Detection:* Classify cluster relationships (`INDEPENDENT`, `DUPLICATE`, `CONNECTED`).
  4. *Root Cause:* Graph traversal and cascade hypothesis synthesis.
  5. *Impact Assessment:* 0–100 threat scoring with factor breakdown.
  6. *Response Planning:* Topologically sorted department work orders.
  7. *Municipal Filing:* Simulated official ticket code generation (`FILE-[INC_ID]`).

### FR-3: Agentic Reasoning & Real-World Tool Calling
- Execute dynamic multi-turn tool calling (Claude) or tool-enriched single-turn reasoning (Groq, OpenAI, Gemini, HF, Ollama):
  - **Open-Meteo Weather API:** Queries 48-hour precipitation forecast to assess drainage overflow risks.
  - **OSM Overpass API:** Locates schools, hospitals, clinics, and kindergartens within 250m to ground hazard scoring.
  - **Civic Dependency Graph:** Evaluates known municipal infrastructure failure linkages.
  - **Historical Incidents Store:** Scans prior repeat failures within 180m.
  - **Haversine Distance Calculator:** Verifies exact spatial distances in meters.

### FR-4: Interactive Operations Dashboard & Spatial GIS Mapping
- Global aggregate metrics: Total Reports, Active Incidents, Critical Priority, Resolved, Reopened, and SLA Escalations.
- **Interactive Leaflet Map View:** Switch seamlessly between List Feed and Spatial Map View with dark/light CartoDB tile layers, cluster radius circles, color-coded priority pins, and sensitive site markers.
- Dynamic feed cards with direct links to active incident details.

### FR-5: Human-in-the-Loop Approval & Anti-Fraud Verification
- Require operator approval for response plans before dispatching field teams (`ACTION_IN_PROGRESS`).
- Support field resolution submission with "After" photo and GPS coordinates.
- Automated Verification Rules:
  - *Pass:* Distance $<100\text{m}$ and photo matches $\implies$ `RESOLVED` status, impact drops to `LOW`.
  - *Location Mismatch:* Distance $>100\text{m} \implies$ `AWAITING_RESOLUTION_EVIDENCE` status.
  - *Failed Repair / Recurring Complaint:* $\implies$ `REOPENED` status.

### FR-6: SLA Deadline Monitoring & Time-Travel Simulation
- Track SLA deadlines per priority level (Critical: 4–12h, High: 12–48h, Medium: 36–72h, Low: 72–120h).
- Provide demo control **Advance Time (+3 Days)** to simulate a 72-hour skip, trigger SLA breach, set status to `ESCALATED`, and display management alert banner.

### FR-7: Multi-Provider AI Settings & Operator Security
- Configure and switch between Groq, OpenAI, Anthropic, Gemini, Hugging Face, OpenRouter, Ollama, and Deterministic Simulation.
- Encrypt API keys at rest using 256-bit Fernet symmetric cryptography (`provider_configs.enc.json`).
- Require `X-Operator-Token` header for settings mutations with 1-click dev token helper for local operators.
- Provide in-flight connection ping diagnostic test displaying response latency (ms).

---

## 6. Non-Functional Requirements

- **Performance:** Full pipeline execution $<2.5\text{s}$ in deterministic offline mode; $<8\text{s}$ in live LLM tool-calling mode.
- **Reliability:** 100% demo availability via graceful fallback to deterministic lookup tables when external APIs are offline or unconfigured.
- **Security:** Zero plaintext key persistence on disk; masked client transmission; operator token authorization.
- **Usability:** Responsive layout with seamless Dark and Light theme toggle, modern glassmorphic cards, and high-contrast status cues.
- **Traceability:** Every decision logged with timestamp, confidence rating, evidence used, and recommending agent in `agent_logs.json`.

---

## 7. Demo Scenarios & Rehearsal Flow

1. **Scenario 1 (Water Infrastructure Cascade):** Water pipe leak near Chakala Junction causing road foundation erosion, pothole formation, and waterlogging (`INC-2026-001`).
2. **Scenario 2 (Drainage-Waste Cycle):** Overflowing garbage bins in Kurla blocking drainage grates and causing street flooding (`INC-2026-002`).
3. **Scenario 3 (Electrical Safety Hazard):** Exposed live electrical wire near a school gate with only 2 reports scored as **CRITICAL Priority (91/100)** threat, demonstrating risk-based prioritization.
4. **Scenario 4 (Recurring Repair Failure):** Road patch failure on Hill Road triggering incident reopening and contractor audit.

