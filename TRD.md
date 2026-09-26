# OmniCivic AI — Technical Requirements Document (TRD)

---

## 1. System Architecture & Tech Stack

### 1.1 Backend Stack
- **Framework:** Python 3.10+ / FastAPI (`0.115.12`)
- **Server:** Uvicorn ASGI (`0.34.3`)
- **Data Validation:** Pydantic v2 (`2.11.3`)
- **Environment Management:** `python-dotenv`
- **Image Processing:** Pillow (`Pillow>=10.0.0`)
- **AI / Multimodal SDKs:** `anthropic==0.53.0`, `google-generativeai` (Optional live integrations with graceful deterministic fallback)

### 1.2 Frontend Stack
- **Framework:** React 19 (`^19.2.7`) with TypeScript (`~6.0.2`)
- **Build System:** Vite (`^8.1.1`)
- **Styling:** Vanilla CSS design tokens + TailwindCSS v4 (`^4.3.2`)
- **Icons & Visuals:** `lucide-react` (`^1.24.0`), `recharts` (`^3.9.2`)
- **Routing:** `react-router-dom` (`^7.18.1`)

---

## 2. Mathematical Algorithms & Core Logic

### 2.1 Geographic Distance Math (Haversine Formula)
The Clustering Agent computes exact spatial proximity between reports without external GIS dependencies:

$$\Delta \phi = \frac{(\text{lat}_2 - \text{lat}_1) \cdot \pi}{180}, \quad \Delta \lambda = \frac{(\text{lon}_2 - \text{lon}_1) \cdot \pi}{180}$$

$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos\left(\frac{\text{lat}_1 \cdot \pi}{180}\right) \cdot \cos\left(\frac{\text{lat}_2 \cdot \pi}{180}\right) \cdot \sin^2\left(\frac{\Delta \lambda}{2}\right)$$

$$c = 2 \cdot \arctan2\left(\sqrt{a}, \sqrt{1-a}\right), \quad d = R \cdot c \quad (R = 6,371,000 \text{ m})$$

*Clustering Threshold:* Distance $d \le 180\text{ meters}$ and Time Window $\Delta t \le 7\text{ days}$.

### 2.2 Civic Impact Score Formula
The Civic Impact Agent calculates a normalized threat score $S \in [0, 100]$:

$$S_{\text{impact}} = 0.30 \cdot S_{\text{severity}} + 0.20 \cdot S_{\text{proximity}} + 0.15 \cdot S_{\text{affected}} + 0.10 \cdot S_{\text{duration}} + 0.10 \cdot S_{\text{repeats}} + 0.15 \cdot S_{\text{risk}}$$

- **Priority Classification Boundaries:**
  - $S \ge 80 \implies \text{CRITICAL}$
  - $65 \le S < 80 \implies \text{HIGH}$
  - $45 \le S < 65 \implies \text{MEDIUM}$
  - $S < 45 \implies \text{LOW}$

### 2.3 Topological Sort for Department Sequencing
The Response Agent executes a dependency-matching topological sort over `departments.json`:
- `WATER_BOARD` & `ELECTRICAL_DEPT` (In-degree = 0) $\to$ First Priority.
- `STORM_WATER_DRAINAGE` (Depends on `SOLID_WASTE_MGMT` / `WATER_BOARD`).
- `ROADS_DEPT` (Depends on `WATER_BOARD` & `STORM_WATER_DRAINAGE`) $\to$ Executed last to prevent paving over active leaks.

---

## 3. Data Models & JSON Schemas

### 3.1 Report Object (`complaints.json`)
```json
{
  "report_id": "CIV-2026-1001",
  "timestamp": "2026-07-01T08:30:00+05:30",
  "citizen_name": "Rajesh Kumar",
  "phone": "+91-98200-10001",
  "location": {
    "latitude": 19.1190,
    "longitude": 72.8470,
    "address": "Near Chakala Junction, Andheri East",
    "ward": "Ward 7 - Andheri East"
  },
  "description": "Major water leak from underground pipe near Chakala junction.",
  "image_filename": "leak_01.jpg",
  "status": "SUBMITTED",
  "linked_incident_id": "INC-2026-001",
  "ward": "Ward 7 - Andheri East",
  "scenario_id": 1
}
```

### 3.2 Incident Context Object (`incidents.json`)
```json
{
  "incident_id": "INC-2026-001",
  "status": "UNDER_REVIEW",
  "classification": "HIGH_CONFIDENCE_CONNECTED",
  "created_at": "2026-08-31T23:00:00+05:30",
  "updated_at": "2026-08-31T23:05:00+05:30",
  "connected_reports": ["CIV-2026-1001", "CIV-2026-1002", "CIV-2026-1003"],
  "cluster": {
    "radius_m": 150.0,
    "time_window_days": 7,
    "center_lat": 19.1191,
    "center_lon": 72.8470,
    "report_count": 6
  },
  "root_cause": {
    "hypothesis": "Underground pipe burst weakening road sub-base",
    "confidence": 0.88,
    "chain": ["WATER_LEAKAGE", "ROAD_DAMAGE", "POTHOLE", "WATERLOGGING"],
    "disclaimer": "AI-generated civic incident hypothesis. Physical inspection recommended."
  },
  "impact_score": {
    "score": 88,
    "priority": "CRITICAL",
    "explanation": "High severity water main leak affecting key junction."
  },
  "response_plan": {
    "approved": false,
    "steps": [
      {
        "step_number": 1,
        "department": "WATER_BOARD",
        "action": "Isolate and repair damaged water main",
        "estimated_hours": 12
      },
      {
        "step_number": 2,
        "department": "ROADS_DEPT",
        "action": "Backfill sub-base and resurface asphalt",
        "estimated_hours": 24
      }
    ]
  }
}
```

---

## 4. API Endpoints Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/reports` | Submit citizen report (handles multipart photo upload or demo image key). |
| `GET` | `/reports` | List all citizen complaints (supports `ward` and `status` query filters). |
| `GET` | `/reports/{id}` | Retrieve single complaint detail. |
| `POST` | `/analyze/{report_id}` | Trigger 7-stage multi-agent pipeline execution. |
| `GET` | `/incidents` | List all structured incident contexts. |
| `GET` | `/incidents/{id}` | Get detailed incident context. |
| `POST` | `/incidents/{id}/approve-plan` | Authority officer human-in-the-loop plan approval. |
| `POST` | `/incidents/{id}/resolution` | Field worker resolution evidence submission. |
| `POST` | `/incidents/{id}/verify-resolution` | Execute Verification Agent on field evidence. |
| `POST` | `/incidents/{id}/advance-demo-time` | Advance SLA timer (+72h) to trigger escalation. |
| `GET` | `/agent-logs` | Retrieve structured agent audit logs. |
| `GET` | `/dashboard/stats` | Retrieve aggregate metric statistics. |
| `POST` | `/dev/reset-demo` | Reset complaints, incidents, and logs to initial seed state. |

---

## 5. Third-Party AI Integration & Fallback Matrix

```
┌─────────────────────────────────────────────────────────────┐
│                      Perception Agent                       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                Is live API key configured?
               ┌───────────────┴───────────────┐
              YES                             NO
               │                               │
    ┌──────────▼──────────┐         ┌──────────▼──────────┐
    │  Gemini 1.5 Flash   │         │ Deterministic Image │
    │  Multimodal API     │         │ Lookup Table        │
    └──────────┬──────────┘         └──────────┬──────────┘
               │                               │
               └───────────────┬───────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                     Root Cause & Impact                     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                Is Anthropic API key configured?
               ┌───────────────┴───────────────┐
              YES                             NO
               │                               │
    ┌──────────▼──────────┐         ┌──────────▼──────────┐
    │ Anthropic Claude    │         │ Graph Knowledge     │
    │ Sonnet Narrative    │         │ Synthesis Fallback  │
    └─────────────────────┘         └─────────────────────┘
```

---

## 6. System SLAs & Performance Constraints

- **Pipeline Latency:** $< 2.5\text{ seconds}$ total pipeline response time in offline fallback mode.
- **Verification Threshold:** Spatial tolerance $< 100\text{ meters}$ between complaint location and resolution photo GPS.
- **Persistence:** Instant atomic write to JSON disk files on every state change.
