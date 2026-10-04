# OmniCivic AI — Technical Requirements Document (TRD)

---

## 1. System Architecture & Tech Stack

### 1.1 Backend Stack
- **Framework:** Python 3.10+ / FastAPI (`0.115.12`)
- **Server:** Uvicorn ASGI (`0.34.3`)
- **Data Validation & Typing:** Pydantic v2 (`2.11.3`)
- **Environment Management:** `python-dotenv` (`1.1.0`)
- **HTTP & Tool Client:** `httpx` (`>=0.27.0`)
- **Image Processing:** Pillow (`Pillow>=10.0.0`)
- **Cryptography & Security:** `cryptography` (Fernet 256-bit symmetric encryption at rest)
- **AI / Multimodal SDKs:**
  - `anthropic` (`0.53.0`) — Multi-turn agentic tool calling
  - `google-generativeai` (`>=0.8.0`) — Multimodal perception and reasoning
  - Native HTTP REST integrations for Groq Cloud, OpenAI ChatGPT, Hugging Face, OpenRouter, and Ollama

### 1.2 Frontend Stack
- **Framework:** React 19 (`^19.2.7`) with TypeScript (`~6.0.2`)
- **Build System & Dev Server:** Vite (`^8.1.1`)
- **Styling:** Vanilla CSS design tokens (`index.css`) + TailwindCSS v4 (`^4.3.2`)
- **Spatial GIS Mapping:** `leaflet` (`^1.9.4`), `react-leaflet` (`^5.0.0`), `@types/leaflet` (`^1.9.22`)
- **Icons & Visuals:** `lucide-react` (`^1.24.0`), `recharts` (`^3.9.2`)
- **Routing:** `react-router-dom` (`^7.18.1`)
- **Linter:** `oxlint` (`^1.71.0`)

---

## 2. Mathematical Algorithms & Core Logic

### 2.1 Geographic Distance Math (Haversine Formula)
The Clustering Agent, Verification Agent, and analytical tools compute spherical surface distances without external GIS dependencies:

$$\Delta \phi = \frac{(\text{lat}_2 - \text{lat}_1) \cdot \pi}{180}, \quad \Delta \lambda = \frac{(\text{lon}_2 - \text{lon}_1) \cdot \pi}{180}$$

$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos\left(\frac{\text{lat}_1 \cdot \pi}{180}\right) \cdot \cos\left(\frac{\text{lat}_2 \cdot \pi}{180}\right) \cdot \sin^2\left(\frac{\Delta \lambda}{2}\right)$$

$$c = 2 \cdot \arctan2\left(\sqrt{a}, \sqrt{1-a}\right), \quad d = R \cdot c \quad (R = 6,371,000\text{ m})$$

- **Clustering Parameters:** Spatial distance $d \le 180\text{ meters}$, Temporal window $\Delta t \le 7\text{ days}$.
- **Resolution Verification Threshold:** Spatial distance $d \le 100\text{ meters}$.

### 2.2 Civic Impact Score Formula
The Civic Impact Agent computes a normalized threat score $S \in [0, 100]$:

$$S_{\text{impact}} = 0.30 \cdot S_{\text{severity}} + 0.20 \cdot S_{\text{proximity}} + 0.15 \cdot S_{\text{affected}} + 0.10 \cdot S_{\text{duration}} + 0.10 \cdot S_{\text{repeats}} + 0.15 \cdot S_{\text{risk}}$$

- **Factor Breakdown & Grounding:**
  - $S_{\text{severity}}$: Inferred issue severity (Critical: 90–100, High: 70–89, Medium: 40–69, Low: 10–39).
  - $S_{\text{proximity}}$: Proximity to high-density zones or sensitive sites discovered via OpenStreetMap (e.g., schools, hospitals $<250\text{m}$).
  - $S_{\text{affected}}$: Estimated population impacted based on transit corridor type and complaint volume.
  - $S_{\text{duration}}$: Elapsed time since the earliest clustered complaint in hours.
  - $S_{\text{repeats}}$: Weight for recurring failure history within 180m from `get_historical_incidents`.
  - $S_{\text{risk}}$: Secondary escalation hazards (e.g. electrocution risk, weather-driven flooding from Open-Meteo).
- **Classification Thresholds:**
  - $S \ge 80 \implies \text{CRITICAL}$
  - $65 \le S < 80 \implies \text{HIGH}$
  - $45 \le S < 65 \implies \text{MEDIUM}$
  - $S < 45 \implies \text{LOW}$

### 2.3 Topological Sorting & Department Dependency Guardrail
The Response Agent executes a dependency-directed topological sort over municipal departments to prevent premature repairs:
1. `WATER_BOARD` & `ELECTRICAL_DEPT` (Underground utility isolation, In-degree = 0) $\to$ First.
2. `SOLID_WASTE_MGMT` $\to$ Clear surface blockages.
3. `STORM_WATER_DRAINAGE` $\to$ Clear drain lines (depends on waste clearing and pipe repairs).
4. `ROADS_DEPT` $\to$ Backfill sub-base and pave asphalt surface (strictly dependent on utilities).

---

## 3. Data Models & JSON Schemas

### 3.1 Report Object Schema (`complaints.json`)
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

### 3.2 Incident Context Schema (`incidents.json`)
```json
{
  "incident_id": "INC-2026-001",
  "status": "UNDER_REVIEW",
  "classification": "HIGH_CONFIDENCE_CONNECTED",
  "reasoning_mode": "agentic_multi_turn",
  "tools_used": [
    "get_weather_forecast",
    "find_nearby_sensitive_sites",
    "query_dependency_graph",
    "get_historical_incidents"
  ],
  "agent_trace": [
    {
      "step": 1,
      "type": "model_call",
      "summary": "Model decided to query weather and sensitive sites",
      "latency_ms": 240
    },
    {
      "step": 2,
      "type": "tool_call",
      "tool": "get_weather_forecast",
      "args": {"latitude": 19.1190, "longitude": 72.8470},
      "result_summary": "0mm precip expected, 28C",
      "latency_ms": 310
    },
    {
      "step": 3,
      "type": "final",
      "summary": "Synthesized root cause and topological response plan",
      "latency_ms": 520
    }
  ],
  "reflection": {
    "verdict": "approved",
    "iterations": 1,
    "issues": [],
    "checks": [
      {"name": "Graph Edge Validity", "passed": true, "detail": "All 3 causal transitions exist in knowledge graph"},
      {"name": "Evidence Grounding", "passed": true, "detail": "3 verified observations grounded in evidence"},
      {"name": "Impact Consistency", "passed": true, "detail": "Computed score 88 matches priority CRITICAL"}
    ]
  },
  "nearby_sites": [
    {
      "id": "site_1",
      "name": "St. Xavier's High School",
      "type": "school",
      "latitude": 19.1198,
      "longitude": 72.8482,
      "distance_m": 154.2
    }
  ],
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
    "evidence": [
      "Water leakage detected at source coordinates (leak_01.jpg)",
      "Road sub-base erosion reported within 45m radius",
      "48h weather forecast indicates 65% rain probability compounding waterlogging"
    ],
    "disclaimer": "AI-generated civic incident hypothesis. Physical inspection recommended.",
    "tools_used": ["get_weather_forecast", "find_nearby_sensitive_sites"]
  },
  "impact_score": {
    "score": 88,
    "priority": "CRITICAL",
    "breakdown": {
      "severity_score": 90,
      "infrastructure_proximity": 85,
      "people_affected": 80,
      "duration": 60,
      "repeat_reports": 70,
      "secondary_risk": 95
    },
    "explanation": "Critical water main failure eroding major transit road near school."
  },
  "response_plan": {
    "approved": false,
    "approved_by": "",
    "approved_at": "",
    "rationale": "Sequenced utility repair prior to road restoration.",
    "steps": [
      {
        "step_number": 1,
        "department": "WATER_BOARD",
        "department_name": "Municipal Water Supply Board",
        "action": "Isolate damaged water main and replace cracked section",
        "estimated_hours": 12,
        "depends_on": []
      },
      {
        "step_number": 2,
        "department": "STORM_WATER_DRAINAGE",
        "department_name": "Stormwater Drainage Dept",
        "action": "Clear debris from adjacent storm drains",
        "estimated_hours": 8,
        "depends_on": ["WATER_BOARD"]
      },
      {
        "step_number": 3,
        "department": "ROADS_DEPT",
        "department_name": "Roads & Traffic Infrastructure",
        "action": "Backfill sub-base and lay asphalt overlay",
        "estimated_hours": 24,
        "depends_on": ["WATER_BOARD", "STORM_WATER_DRAINAGE"]
      }
    ]
  },
  "resolution": {
    "before_photo": "leak_01.jpg",
    "after_photo": "",
    "verification_result": "PENDING",
    "verification_details": "",
    "confidence": 0.0
  },
  "sla": {
    "deadline": "2026-09-01T11:00:00+05:30",
    "reminders_sent": 0,
    "escalated": false,
    "escalation_reason": ""
  }
}
```

---

## 4. API Endpoints Specification

| Method | Endpoint | Auth Header | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/reports` | None | Submit citizen report (handles multipart photo upload or demo image selection). |
| `GET` | `/reports` | None | List citizen complaints with optional `ward` or `status` filters. |
| `GET` | `/reports/{id}` | None | Retrieve single complaint report. |
| `POST` | `/analyze/{report_id}` | None | Execute full 7-stage multi-agent analysis pipeline. |
| `GET` | `/incidents` | None | List all structured incident contexts. |
| `GET` | `/incidents/{id}` | None | Get complete incident context object. |
| `POST` | `/incidents/{id}/analyze` | None | Re-run agentic reasoning pipeline on an existing incident. |
| `GET` | `/incidents/{id}/impact` | None | Get impact score breakdown. |
| `GET` | `/incidents/{id}/response-plan` | None | Get sequenced department work orders. |
| `POST` | `/incidents/{id}/approve-plan` | None | Human-in-the-loop: Approve response plan and advance to `ACTION_IN_PROGRESS`. |
| `POST` | `/incidents/{id}/resolution` | None | Field worker resolution evidence submission ("After" photo + GPS coordinates). |
| `POST` | `/incidents/{id}/verify-resolution` | None | Run Resolution Verification Agent on submitted evidence. |
| `POST` | `/incidents/{id}/advance-demo-time` | None | Advance SLA clock (+72 hours) to simulate escalation. |
| `GET` | `/dashboard/stats` | None | Retrieve aggregate dashboard metrics. |
| `GET` | `/agent-logs` | None | Retrieve centralized agent audit logs with optional filters. |
| `GET` | `/seed-images/{filename}` | None | Serve seed evidence images with `.jpg` / `.png` fallback. |
| `GET` | `/dev/seed-images` | None | List available demonstration evidence photos. |
| `GET` | `/dev/scenarios` | None | List preset demo scenarios. |
| `GET` | `/dev/perception-lookup` | None | Retrieve perception lookup catalog. |
| `POST` | `/dev/reset-demo` | None | Reset database and state files to pristine seed state. |
| `GET` | `/api/settings/dev-token` | None | Development helper returning active local operator token for 1-click UI auth. |
| `GET` | `/api/settings` | `X-Operator-Token` | Retrieve provider configs (with masked keys) and active provider. |
| `POST` | `/api/settings` | `X-Operator-Token` | Save/update provider config with Fernet encryption and overwrite protection. |
| `POST` | `/api/settings/set-active` | `X-Operator-Token` | Switch active LLM provider without altering stored credentials. |
| `DELETE` | `/api/settings/provider/{id}` | `X-Operator-Token` | Delete stored credentials for a provider. |
| `POST` | `/api/settings/test` | `X-Operator-Token` | Execute 10s ping diagnostic test returning round-trip latency (ms). |
| `GET` | `/geocode` | None | Free OSM Nominatim geocoding proxy with rate-limiting, 1h cache & offline fallback. |
| `GET` | `/health` | None | Service liveness probe. |

---

## 5. Third-Party AI Integration & Tool-Loop Fallback Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Agentic Reasoning Engine Routing                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                     Check active_provider in Settings
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
 ┌──────────────┐           ┌──────────────┐           ┌──────────────┐
 │ Anthropic    │           │ OpenAI / Groq│           │ Mock /       │
 │ Claude SDK   │           │ OpenRouter / │           │ Keyless      │
 │ tool_use     │           │ Ollama / Gem │           │ Deterministic│
 └──────┬───────┘           └──────┬───────┘           └──────┬───────┘
        │                          │                          │
        ├──────────────────────────┘                          │
        ▼                                                     ▼
┌──────────────────────────────────────┐            ┌──────────────────┐
│ Provider-Agnostic Tool Loop          │            │ Deterministic    │
│ (tool_loop.py)                       │            │ Pathfinder &     │
│ • Max 6 turns, 8s total timeout      │            │ Causal Tables    │
│ • Model dynamically selects tools    │            │ (100% Offline,   │
│ • Dynamic retry & step tracing       │            │  < 10ms execution│
└──────────────────┬───────────────────┘            └─────────┬────────┘
                   │                                          │
                   └─────────────────────┬────────────────────┘
                                         ▼
                             ┌───────────────────────┐
                             │ Critic / Reflection   │
                             │ (critic.py)           │
                             │ • 6 Validation Checks │
                             │ • Max 1 Revision Pass │
                             └───────────────────────┘
```

---

## 6. Security, Resilience & Environment Flags

- **Encryption at Rest:** Symmetric Fernet 256-bit cipher encrypting `provider_configs.enc.json`. Key resolution: `LLM_ENCRYPTION_KEY` env var $\to$ `backend/.secret.key` file.
- **Operator Authorization:** Settings endpoints enforce `verify_operator_token`. Unauthenticated requests return `401 Unauthorized`.
- **Transient Error Resilience:** Automatic 1-retry with 1.0s backoff for transient network timeouts (HTTP 429, 500, 502, 503, 504).
- **Latency SLAs:** Offline execution $<2.5\text{s}$; external live tool execution $<8.0\text{s}$ with 6-8s client timeouts.
- **Environment Flags:**
  - `ENABLE_DEV_ENDPOINTS`: (`"true"` | `"false"`, default `"true"`) Controls accessibility of development helper endpoints (`/api/settings/dev-token`, `/dev/reset-demo`). Returns HTTP 403 Forbidden in production environments when disabled.
  - `SIMULATE_TOOL_FAILURE`: (`"weather"` | `"osm"` | `"all"`) Development & testing flag that forces simulated external tool failures/timeouts, verifying graceful degradation, confidence reductions, and error tracing in `agent_trace`.

