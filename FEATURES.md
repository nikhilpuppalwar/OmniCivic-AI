# OmniCivic AI — Feature Specifications

---

## 1. Feature Overview Matrix

| Feature | Key Functionality | Target User | Component / Route |
| :--- | :--- | :--- | :--- |
| **Citizen Complaint Reporting** | Upload photos, select ward, provide description and geo-coordinates. | Citizen | `/submit-report` |
| **Agentic Pipeline Execution** | One-click 7-stage autonomous AI analysis trigger. | Operator | `/analyze/{report_id}` |
| **Cascading Root Cause Graph** | Identifies origin failure causing multiple downstream issues. | Ward Officer | `RootCauseCard.tsx` |
| **Civic Impact Priority Gauge** | Real-time 0–100 threat score gauge with factor breakdown. | Operator | `ImpactGauge.tsx` |
| **Sequenced Department Plan** | Sequenced execution order preventing re-repair loops. | Dept Lead | `ResponsePlanCard.tsx` |
| **Human-in-the-Loop Approval** | Official sign-off before dispatching department teams. | Authority | `approvePlan()` API |
| **Verification Gate** | Dual-check GPS distance (<100m) & visual match on "After" photos. | Field Officer | `VerificationCard.tsx` |
| **SLA Time-Travel Escalator** | Demo button (+72h) triggering SLA breach & priority escalation. | Operator / Demo | `advanceDemoTime()` API |
| **Transparent Audit Trace** | Real-time agent decision log with confidence scores and evidence used. | Operator | `AgentLogDrawer.tsx` |

---

## 2. Feature Deep Dives

### Feature 1: Citizen Complaint Reporting
- **User Action:** Citizens fill out a report form containing location details, ward selection, description, and photo evidence (via live file upload or pre-seeded demo image).
- **System Action:** Validates MIME type (`image/jpeg`, `image/png`, `image/webp`), assigns unique report ID (`CIV-2026-1051`), stores photo in `uploads/reports/`, and persists report object to `complaints.json`.

### Feature 2: Autonomous Multi-Agent Pipeline Execution
- **User Action:** Operator clicks **Run Agentic AI** on any report card in the Citizen Reports Feed.
- **System Action:** Sequentially executes all 7 pipeline agents in under 3 seconds:
  1. *Perception Agent:* Classifies issue type and extracts visual features.
  2. *Clustering Agent:* Groups reports within 180m and 7 days.
  3. *Incident Detection Agent:* Evaluates cluster relationship rules.
  4. *Root Cause Agent:* Traverses causal graph to detect underlying origin failure.
  5. *Impact Agent:* Computes threat score (0-100) and priority level (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
  6. *Response Agent:* Generates topologically sorted multi-department work orders.
  7. *Filing Agent:* Produces official municipal filing ticket code (`FILE-[INC_ID]`).

### Feature 3: Cascading Root-Cause Graph Intelligence
- **Function:** Solves the core problem of fixing surface symptoms while ignoring hidden underlying failures.
- **Example Scenario (Scenario 1):**
  - Leaking underground pipe near Chakala Junction (*Water Board*) $\to$
  - Water seepage weakens road sub-base (*Roads Dept*) $\to$
  - Traffic creates deep potholes (*Roads Dept*) $\to$
  - Potholes trap rainwater causing severe waterlogging (*Drainage Dept*).
- **Output:** Clearly presents the root cause hypothesis alongside the mandatory safety disclaimer:
  > *"AI-generated civic incident hypothesis. Physical inspection recommended."*

### Feature 4: Civic Impact Priority Gauge
- **Function:** Replaces simple complaint count with an objective threat score (0–100).
- **Weighted Factors:**
  - Issue Severity (30%)
  - Infrastructure Proximity (20%)
  - Estimated People Affected (15%)
  - Issue Duration (10%)
  - Repeat Complaint Count (10%)
  - Secondary Hazard Risks (15%)
- **Value Demonstration (Scenario 3):** Identifies an exposed live electrical wire near a school with only 2 reports as a **CRITICAL Priority (91/100)** threat, overriding high-volume but low-risk complaints.

### Feature 5: Sequenced Response Plan with Human Approval
- **Function:** Enforces mandatory execution order across municipal departments.
- **Human-in-the-Loop Gate:** Response plan remains in `PENDING` state until an authorized municipal officer clicks **Approve Multi-Department Plan**. Upon approval, status transitions to `ACTION_IN_PROGRESS` and timestamps are logged.

### Feature 6: Verification Agent & Anti-Fraud Gate
- **Function:** Prevents contractors from closing tickets with invalid or fake resolution evidence.
- **Evaluation Rules:**
  1. **GPS Proximity Check:** Computes Haversine distance between original complaint location and "After" photo GPS coordinates. If distance $> 100\text{ meters}$, returns **`LOCATION_MISMATCH`** and refuses to close ticket.
  2. **Visual Feature Match:** Compares issue categories. If "After" photo depicts a different category (e.g., submitting garbage photo for a water leak), flags mismatch.
  3. **Verification Outcome:** Only when distance $< 100\text{m}$ and photo matches does status become **`RESOLVED`**, automatically lowering impact priority to `LOW`.

### Feature 7: SLA Escalation & Time-Travel Simulation
- **Function:** Demonstrates automated management escalation when field teams fail to meet SLA deadlines.
- **SLA Thresholds:**
  - Critical: 4 – 12 Hours
  - High: 12 – 48 Hours
  - Medium: 36 – 72 Hours
  - Low: 72 – 120 Hours
- **Demo Control:** Clicking **Advance Time (+3 Days)** simulates a 72-hour time skip, immediately triggering SLA expiration, updating status to `ESCALATED`, and issuing an emergency escalation notification to senior management.
