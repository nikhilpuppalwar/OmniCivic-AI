# OmniCivic AI — Feature Specifications

---

## 1. Feature Overview Matrix

| Feature | Key Functionality | Target User | Component / Route |
| :--- | :--- | :--- | :--- |
| **Citizen Complaint Reporting** | Live file upload (JPG/PNG/WEBP), map picker, GPS detection, and demo presets. | Citizen | `/report` (`CitizenReport.tsx`) |
| **Multi-Agent Pipeline Execution** | One-click 7-stage autonomous AI analysis orchestrating 10 specialized agents. | Operator | `/analyze/{report_id}` (`AgentPipeline.tsx`) |
| **Agentic Reasoning & Tool Loop** | Multi-turn tool calling: Open-Meteo weather, OSM sensitive sites, causal graph, history. | System / AI | `reasoning_agent.py` & `external_tools.py` |
| **Cascading Root Cause Graph** | Causal dependency traversal identifying underlying root-cause infrastructure failures. | Ward Officer | `RootCauseCard.tsx` |
| **Civic Impact Priority Gauge** | 0–100 threat score based on 6 weighted factors, grounded with live GIS data. | Operator | `ImpactGauge.tsx` |
| **Spatial GIS & Leaflet Mapping** | Interactive map with cluster radii, priority pins, and sensitive facility markers. | Operator / Lead | `MapView.tsx` |
| **Sequenced Department Plan** | Topologically sorted multi-department work orders preventing re-repair loops. | Dept Lead | `ResponsePlan.tsx` |
| **Human-in-the-Loop Approval** | Official operator sign-off before dispatching department repair crews. | Authority Officer | `approvePlan()` API |
| **Resolution Verification Gate** | Anti-fraud dual-check: GPS distance (<100m) and post-repair visual matching. | Field Officer | `ResolutionPanel.tsx` |
| **SLA Time-Travel Escalator** | Demo button (+72h) triggering SLA expiration and senior management escalation. | Operator / Demo | `DemoControls.tsx` |
| **Multi-Provider AI Settings** | Manage Groq, OpenAI, Claude, Gemini, HF, Ollama with Fernet encryption & ping test. | Operator | `/settings` (`Settings.tsx`) |
| **Operator Token Authorization** | Security token validation (`X-Operator-Token`) protecting configuration endpoints. | Security Admin | `verify_operator_token` |
| **Light & Dark Mode Command Center** | Theme switching with CartoDB Dark/Light map tiles and glassmorphism tokens. | All Users | `ThemeContext.tsx` |

---

## 2. Feature Deep Dives

### Feature 1: Citizen Complaint Submission Portal (`CitizenReport.tsx`)
- **Dual Input Modes:**
  1. *Live File Upload Mode:* Drag-and-drop or file selector supporting `image/jpeg`, `image/png`, `image/webp`. Enforces server-side MIME type verification and generates unique UUID filenames stored in `backend/uploads/reports/`. Includes GPS coordinate auto-detection (`navigator.geolocation`) and an interactive Leaflet map coordinate picker.
  2. *Preset Demo Scenarios:* Quick-select buttons for pre-calibrated demo incidents (`leak_01.jpg`, `road_damage_01.jpg`, `pothole_01.jpg`, `waterlogging_01.jpg`, `exposed_wire_01.jpg`, `garbage_01.jpg`, `drain_01.jpg`) with pre-filled coordinates and ward metadata.
- **Immediate Analysis Handoff:** Upon submission, provides a direct CTA to navigate to the Operations Dashboard with `autoAnalyzeId` state to trigger the pipeline automatically.

### Feature 2: Autonomous Multi-Agent Pipeline Execution (`AgentPipeline.tsx`)
- **Single-Click Orchestration:** Triggered by clicking **Run Agentic AI** on any pending report card.
- **7-Stage Visual Pipeline:**
  1. *Perception Agent:* Classifies primary issue category and extracts visual evidence.
  2. *Clustering Agent:* Groups reports within 180 meters and a 7-day temporal window.
  3. *Batch Perception & Incident Detection:* Analyzes all clustered reports and classifies relationship type (`HIGH_CONFIDENCE_CONNECTED`, `POSSIBLE_CONNECTED`, `DUPLICATE`, `INDEPENDENT`).
  4. *Root Cause Agent:* Traverses causal graph to detect origin breakdown.
  5. *Civic Impact Agent:* Calculates weighted 0–100 threat score and priority level (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
  6. *Response Agent:* Generates topologically sorted multi-department work orders.
  7. *Filing Agent:* Produces official simulated municipal filing tracking code (`FILE-[INC_ID]`).
- **Telemetry & Logging:** Real-time progress bar, stage duration indicators, confidence metrics, and atomic updates to `agent_logs.json`.

### Feature 3: Agentic Reasoning Engine & Provider-Agnostic Tool Loop (`reasoning_agent.py`, `tool_loop.py`)
- **Autonomous Multi-Turn Tool Calling:** Provider-neutral canonical tool schema translated dynamically to native function calling across Anthropic Claude (`tool_use`), OpenAI / Groq / OpenRouter (`tools` array), and Google Gemini (`functionDeclarations`). The LLM autonomously chooses which tools to call, in what sequence, and when to stop (budget: max 6 turns, 8.0s timeout).
- **Graceful 3-Tier Degradation:**
  1. `agentic_multi_turn`: Autonomous multi-turn tool calling loop.
  2. `single_turn_enriched`: Prompt enrichment with pre-called analytical tools.
  3. `deterministic_fallback`: 100% offline knowledge-graph pathfinding and formula evaluation (<10ms).
- **Honest Telemetry:** System explicitly records `reasoning_mode` on the incident without masking fallback.
- **5 Keyless Analytical Tools:**
  - 🌧️ *Open-Meteo Weather API (`get_weather_forecast`):* 48-hour hourly precipitation probability and rain volume (mm).
  - 🏫 *OSM Overpass API (`find_nearby_sensitive_sites`):* Queries OpenStreetMap for schools, hospitals, clinics, transit hubs (<250m).
  - 📊 *Civic Dependency Graph (`query_dependency_graph`):* Queries curated failure dependencies from `civic_dependencies.json`.
  - 📜 *Historical Incident Lookup (`get_historical_incidents`):* Checks prior incidents within 180m for chronic failures.
  - 📏 *Haversine Calculator (`compute_distance`):* Computes exact coordinate distances in meters.

### Feature 4: Cascading Root-Cause Intelligence & Self-Critique Reflection (`RootCauseCard.tsx`, `critic.py`)
- **Self-Critique & Reflection Agent:** Evaluates reasoning drafts against 6 deterministic rubric checks:
  1. Graph Edge Validity against `civic_dependencies.json`.
  2. Evidence Grounding against verified perceptual and tool outputs.
  3. Confidence Boundedness against evidence density.
  4. Impact Formula Mathematical Consistency ($0.30/0.20/0.15/0.10/0.10/0.15$).
  5. Sensitive Facility Reflection for sites $<250\text{m}$.
  6. Response Plan Topological Sequencing feasibility.
- **Autonomous Revision Pass:** If any critical check fails, the critic triggers a targeted revision pass. If issues remain, marks `reflection.verdict = "unresolved"` and downgrades confidence.
- **Interactive UI Presentation:** Glowing root cause node, true 3-state `reasoning_mode` badge, dynamic tool badges, and collapsible Critic Reflection details with pass/fail check status.

### Feature 10: Multi-Provider AI Settings & Security Hardening (`Settings.tsx`)
- **Supported Providers:** Groq Cloud, OpenAI ChatGPT, Anthropic Claude, Google Gemini, Hugging Face, OpenRouter, Ollama, and Deterministic Simulation.
- **Fernet 256-bit Key Encryption:** Encrypts credentials at rest in `backend/data/provider_configs.enc.json`.
- **Operator Token Authorization:** Endpoints guarded by `X-Operator-Token` header.
- **In-Flight Diagnostic Ping:** 10-second ping test button measuring round-trip latency in milliseconds.
- **Key Masking & Overwrite Protection:** Displays masked keys (`sk-...1234`) while preserving plaintext on save.

### Feature 11: Quantitative Evaluation Harness & Ablation Framework (`eval/run_eval.py`)
- **20 Ground-Truth Labeled Benchmarks (`eval/cases.json`):** Covers root-cause cascades, pure duplicates, hard negatives (unrelated co-located reports), school hazards, cosmetic complaints, and recurring structural failures.
- **Automated Mode Ablation:** Compares Deterministic Fallback, Deterministic + Critic, Single-Turn Enriched, and Agentic Multi-Turn across 8 quantitative metrics (Root Cause Acc, Jaccard Index, Priority Acc, Topological Feasibility, False-Connection Rate, Latency).
- **Offline CLI Execution:** Run anytime via `python -m eval.run_eval --mode deterministic` with zero API keys or network dependencies.
- **Reproducible Metrics Report:** Generates `eval/results.json` and `eval/RESULTS.md` with measured numbers.

### Feature 12: Tool Execution Trace & Behavior Inspector (`ToolTraceCard.tsx`)
- **Interactive Trace Inspector:** Expandable timeline revealing every step taken by the autonomous agent: model calls, tool calls, arguments, latency in ms, result summaries, and error handling.
- **Failure Resilience Indicators:** Clearly highlights handled tool errors (e.g. timeout fallback) and display status.

### Feature 13: Failure-Mode Simulation & Ambiguous Case Disambiguation
- **Tool Failure Simulation (`SIMULATE_TOOL_FAILURE=weather|osm|all`):** Tests system resilience against third-party API outages; verifies that the pipeline finishes reliably with reduced confidence and visible error annotations.
- **Scenario 5 (Co-Located Ambiguous Case):** Demonstrates intelligent discrimination between simultaneous, co-located yet non-causal reports (broken streetlight vs overflowing garbage at Dadar Station Plaza), preventing false incident merges.

### Feature 14: Free Address Search & Geocoding with Interactive Map Pinning (`CitizenReport.tsx`, `/geocode`)
- **OpenStreetMap Nominatim Backend Proxy:** Exposes `GET /geocode?q=...` with rate-limiting ($\ge 1\text{s}$ spacing), descriptive `User-Agent`, 1-hour in-memory cache, and local municipal fallback landmarks.
- **Debounced Address Search (>= 500ms):** Responsive input providing live matching suggestions for streets, landmarks, and transit junctions.
- **Interactive Leaflet Pin Picker:** Selecting an address flies the map to the location and drops a draggable pin; clicking anywhere on the map or dragging the pin directly updates coordinates.
- **Offline & Fallback Resilience:** If Nominatim is unreachable, displays a friendly notice and allows users to continue via GPS auto-detect or manual map pinning; offline demo presets remain 100% functional.


