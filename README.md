# OmniCivic AI — Autonomous Civic Incident Intelligence System

> **Tagline:** "Different complaints. One hidden signal."  
> **Framing Line:** "Cities don't have a shortage of complaints. They have a shortage of intelligence connecting those complaints."

OmniCivic AI is a multi-agent civic incident intelligence system designed for municipal operators, ward officers, and citizens to detect, correlate, prioritize, and verify civic infrastructure incidents. By evaluating spatial and temporal proximity across independent citizen reports, OmniCivic AI uncovers cascading root-cause infrastructure failures (e.g., an underground water pipe burst undermining the road sub-base to cause potholes that trap rainwater into traffic-blocking waterlogging), automatically sequences multi-department resolution plans, queries live external civic tools, and validates field resolution outcomes with automated GPS and image verification.

---

## 🛠️ Multi-Agent Architecture & Reasoning Engine

OmniCivic AI operates via a coordinated pipeline of ten specialized backend agents coupled with an **Agentic Reasoning Engine** that performs dynamic multi-turn tool calling and external analytical enrichment.

| Agent | Responsibility | Technical Execution |
| :--- | :--- | :--- |
| **Perception Agent** | Analyzes photos and text descriptions to detect issue category, severity, and visual features. | Gemini Multimodal API or Deterministic Perception Lookup Table (`perception_lookup.json`). |
| **Clustering Agent** | Groups geographically and temporally related reports. | Pure Python Haversine distance ($d \le 180\text{m}$) and time window ($\Delta t \le 7\text{ days}$) math. |
| **Incident Detection Agent** | Analyzes cluster relationships to classify incident scope. | Deterministic rules (`INDEPENDENT`, `DUPLICATE`, `POSSIBLE_CONNECTED`, `HIGH_CONFIDENCE_CONNECTED`). |
| **Agentic Reasoning Engine** | Drives root-cause causal hypothesis, impact scoring, and response sequencing with tool execution. | Multi-turn tool-calling loop (Claude) or single-turn tool enrichment (Groq, OpenAI, Gemini, HF, OpenRouter, Ollama) with deterministic fallback. |
| **Root-Cause Agent** | Traces causal dependencies between distinct civic breakdowns. | Causal graph traversal (`civic_dependencies.json`) + LLM cascade hypothesis synthesis. |
| **Civic Impact Agent** | Scores real-world public threat severity (0–100 scale). | Multi-factor weighted formula (Severity 30%, Proximity 20%, Impacted 15%, Duration 10%, Repeats 10%, Risks 15%) enriched with live OSM and weather data. |
| **Response Agent** | Designates multi-department resolution steps. | Topological dependency sort enforcing mandatory order (e.g. utilities before road resurfacing). |
| **Filing Agent** | Generates formal, traceable municipal filings. | Produces official filing context code `FILE-[INC_ID]` marked as simulated. |
| **Escalation Agent** | Tracks SLA deadlines and alerts management. | State machine transitioner checking SLA expiration + time-travel trigger (+72h). |
| **Verification Agent** | Validates resolution claims via photographic and GPS proof. | Dual-check: Haversine distance threshold ($<100\text{m}$) + post-repair visual evidence matching. |
| **Orchestrator** | Central controller and state coordinator. | Sole writer persisting atomic updates to `incidents.json` and centralized `agent_logs.json`. |

---

## 🌐 External Analytical Tools & Knowledge Sources

When analyzing an incident cluster, the reasoning engine invokes real-world, keyless analytical tools:

- 🌧️ **Open-Meteo Weather API (`get_weather_forecast`):** Retrieves 48-hour precipitation probability and rainfall volume to evaluate drainage overflow and waterlogging risks.
- 🏫 **OSM Overpass API (`find_nearby_sensitive_sites`):** Queries OpenStreetMap for schools, hospitals, clinics, and kindergartens within radius (e.g., 250m) to ground proximity hazard scoring.
- 📊 **Civic Dependency Graph (`query_dependency_graph`):** Queries curated causal linkages between municipal issue types.
- 📜 **Historical Incident Store (`get_historical_incidents`):** Scans prior incidents within 180m to detect recurring infrastructure failures.
- 📏 **Haversine Distance Calculator (`compute_distance`):** Computes precise distance between coordinates in meters.

---

## ⚡ Multi-Provider LLM & Security Hardening

OmniCivic AI includes a built-in **Multi-Provider LLM Manager** (`backend/services/llm_manager.py`) with support for:

- **Groq Cloud:** Ultra-fast LPU inference (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`, `deepseek-r1-distill-llama-70b`)
- **OpenAI (ChatGPT):** Function calling & structured reasoning (`gpt-4o-mini`, `gpt-4o`, `o3-mini`, `o1`)
- **Anthropic Claude:** Full multi-turn agentic tool calling (`claude-3-5-sonnet-20241022`, `claude-3-7-sonnet-20250219`, `claude-3-5-haiku-20241022`, `claude-3-opus-20240229`)
- **Google Gemini:** Multimodal Flash & Pro reasoning (`gemini-flash-latest`, `gemini-pro-latest`, `gemini-2.5-flash`, `gemini-2.5-pro`)
- **Hugging Face Inference API:** Open-weights router with custom model support
- **OpenRouter:** Universal multi-model gateway
- **Ollama / Local Custom:** Self-hosted local inference (`http://localhost:11434`)
- **Deterministic Simulation (Mock):** 100% offline, zero-latency fallback requiring no API keys

### 🔒 Security Features
- **Fernet 256-bit Encryption at Rest:** All API credentials stored in `backend/data/provider_configs.enc.json` are encrypted using symmetric Fernet keys (`LLM_ENCRYPTION_KEY` or `.secret.key`).
- **Operator Token Authorization:** Operator settings endpoints require the `X-Operator-Token` header. An auto-generated token is printed to console on startup and saved to `.operator_token`.
- **Credential Masking & Protection:** Keys returned to the client are masked (`sk-...1234`). Saving configs preserves stored plaintext keys if masked values are sent.
- **In-Flight Diagnostic Ping:** Test provider latency (ms) and verify model connections directly from the UI without changing active configuration.

---

## 🚀 Quick Startup & Execution Guide

### 📋 Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- **Optional API Key:** Any supported provider (Groq, Anthropic, Gemini, OpenAI, etc.). Zero keys needed in default Deterministic Simulation mode.

---

### 🏃 How to Run the Project (Step-by-Step)

#### 1. Backend Service (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Create & activate a virtual environment
python -m venv venv

# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Seed initial complaints, scenarios & lookup tables
python -m scripts.seed_data

# Start the FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend Base URL:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`
- **Operator Token:** Check the terminal banner or `backend/.operator_token` for the operator authorization key.

#### 2. Frontend Application (React + Vite)
```bash
# Open a separate terminal and navigate to frontend directory
cd frontend

# Install Node modules
npm install

# Start Vite development server
npm run dev
```
- **Frontend Overview & Landing Screen:** `http://localhost:5173`
- **Operations Dashboard:** `http://localhost:5173/dashboard`
- **Citizen Report Portal:** `http://localhost:5173/report`
- **AI Settings Manager:** `http://localhost:5173/settings`

---

## 🎯 Rehearsed Live Demo Script

Follow this script step-by-step for a complete demonstration:

1. **Submit Citizen Report (`/report`)**:
   - Go to **Citizen Portal** (`/report`).
   - Choose **Preset Demo Scenarios** or **Live Photo Upload**.
   - Select **`leak_01.jpg`** (Water Leakage near Chakala Junction). Notice coordinates and description auto-fill.
   - Click **Submit Complaint Report**, then click **Go to Dashboard and Analyze**.
2. **Watch Autonomous Multi-Agent Pipeline (`/`)**:
   - The Operations Dashboard receives the report (`CIV-2026-1001`).
   - The **Multi-Agent Reasoning Pipeline** animates through all 7 stages: *Perception* $\to$ *Clustering* $\to$ *Detection* $\to$ *Root Cause* $\to$ *Impact* $\to$ *Response* $\to$ *Filing*.
3. **Inspect Spatial Intelligence & Leaflet Map**:
   - Toggle from **List View** to **Map View** in the Spatial Intelligence feed.
   - Inspect cluster boundaries, citizen complaint pins, and nearby sensitive sites (schools/hospitals).
4. **Examine Root-Cause Hypothesis & Priority Score**:
   - Inspect the **Root Cause Investigation** card showing the causal chain: `WATER_LEAKAGE` $\to$ `ROAD_DAMAGE` $\to$ `POTHOLE` $\to$ `WATERLOGGING`.
   - Check the safety disclaimer: *"AI-generated civic incident hypothesis. Physical inspection recommended."*
   - Inspect the **Civic Impact Priority Gauge** displaying a 0–100 threat score (e.g., Critical 88/100) with 6-factor weight breakdown.
5. **Approve Sequenced Response Plan (Human-in-the-Loop)**:
   - Review the **Multi-Department Response Plan** (Water Board first, Drainage second, Roads Dept last).
   - Click **Approve Multi-Department Plan** to transition status to `ACTION_IN_PROGRESS`.
6. **Test Anti-Fraud Resolution Verification**:
   - In the **Resolution Verification** card, select **Attempt 1: Mismatched Photo** (`resolved_leak_wrong.jpg` located at distant GPS). Click **Submit & Verify**.
   - The Verification Agent flags **`LOCATION_MISMATCH`** ($>100\text{m}$) and rejects closure.
   - Switch to **Attempt 2: Correct Evidence** (`resolved_leak_correct.jpg` at Chakala Junction). Click **Submit & Verify**.
   - The Verification Agent confirms **`RESOLUTION_VERIFIED`**, sets status to **`RESOLVED`**, and lowers impact priority to **`LOW`**.
7. **Simulate SLA Time-Travel Escalation**:
   - Select any active incident and click **Advance Time (+3 Days)** in the header controls.
   - The Escalation Agent simulates a 72-hour skip, triggers SLA expiration, sets status to **`ESCALATED`**, and fires a management escalation alert.
8. **Configure Live AI Providers (`/settings`)**:
   - Navigate to **AI Settings** (`/settings`).
   - Use the 1-click **Authorize Dev Token** button.
   - Switch between **Groq**, **OpenAI**, **Anthropic Claude**, **Gemini**, or **Deterministic Simulation**.
   - Run a live diagnostic ping test with latency metrics.

---

## 🔧 Maintenance, Testing & Evaluation Commands

| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Run Unit Test Suite** | `python -m pytest tests/` (in `backend/`) | Tests provider-agnostic tool loop, budget/timeouts, and critic checks. |
| **Run Evaluation Harness** | `python -m eval.run_eval --mode deterministic` (in `backend/`) | Runs 20-case quantitative benchmark; produces `eval/results.json` & `RESULTS.md`. |
| **Reset Demo State** | `python -m scripts.seed_data` (in `backend/`) | Re-initializes all seed reports, incidents, and logs. |
| **Test Full Pipeline** | `python -m scripts.test_pipeline` (in `backend/`) | CLI verification of the end-to-end multi-agent pipeline. |
| **Test Upload & Pipeline** | `python -m scripts.test_upload_pipeline` | Validates multipart upload handling & analysis. |
| **Test Provider Fallback** | `python -m scripts.test_settings_and_fallback` | Validates encryption, masking, and fallback routing. |
| **Frontend Production Build** | `npm run build` (in `frontend/`) | Type-checks (`tsc -b`) and bundles static assets with Vite. |

---

*Disclaimer: Prototype uses synthetic municipal data for demonstration purposes. All root-cause outputs are AI-generated civic incident hypotheses requiring physical verification.*

