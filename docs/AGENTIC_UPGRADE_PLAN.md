# OmniCivic AI — Agentic Upgrade Implementation Plan

## 1. Overview & Baseline State

This document outlines the detailed architectural upgrade plan for OmniCivic AI to transition from pre-packaged tool execution to a fully autonomous, provider-agnostic agentic tool-calling loop, self-critique/reflection mechanism, and quantitative evaluation harness.

### Baseline Test Results (Captured Before Any Modifications)
- `python -m scripts.test_pipeline`: **PASSED** (Exit Code 0). 7 stages completed, incident INC-2026-001 created.
- `python -m scripts.test_settings_and_fallback`: **PASSED** (Exit Code 0). All 6 automated verification checks passed.
- `python -m scripts.test_upload_pipeline`: **PASSED** (Exit Code 0). Multipart upload and single report pipeline execution successful.
- `npm run build`: **PASSED** (Exit Code 0). 1847 modules transformed, 0 TypeScript errors.

---

## 2. Hard Constraints & Architectural Invariants
1. **Deterministic Offline Mode:** Zero network/API key dependency must complete the full pipeline in $<2.5\text{s}$.
2. **Orchestrator Centrality:** `orchestrator.py` remains the sole writer to `incidents.json` and `agent_logs.json`.
3. **Additive Schema Changes:** All schema additions (`agent_trace`, `reflection`, `requested_evidence`) are strictly optional/additive; legacy incidents load without errors.
4. **Safety & Security:** Preserve Fernet 256-bit key encryption, `X-Operator-Token` protection, credential masking, and the mandatory civic hypothesis safety disclaimer.
5. **Keyless Tools:** Open-Meteo, OSM Overpass, and local state queries remain keyless.

---

## 3. Implementation Breakdown by Phase

### Phase 1: Provider-Agnostic Agentic Tool Loop (Task 1)
- **New Module:** `backend/services/tool_loop.py`
  - Canonical provider-neutral tool schemas for 5 tools (`get_weather_forecast`, `find_nearby_sensitive_sites`, `query_dependency_graph`, `get_historical_incidents`, `compute_distance`).
  - Schema adapters for Anthropic (`tool_use`), OpenAI/Groq/OpenRouter/Ollama (`tools/functions`), and Gemini (`function_declarations`).
  - Unified asynchronous execution loop: Prompt $\to$ Tool Calls $\to$ Execute $\to$ Return Results $\to$ Iterate (max 6 iterations, 8s total timeout).
  - Telemetry capture: `agent_trace` step sequence with latencies, errors, and argument summaries.
  - Three distinct reasoning modes: `"agentic_multi_turn"`, `"single_turn_enriched"`, `"deterministic_fallback"`.
- **Unit Test:** `backend/tests/test_tool_loop.py` (scripted fake provider with zero network).

### Phase 2: Critic / Reflection Agent (Task 2)
- **New Module:** `backend/agents/critic.py`
  - Validates draft against dependency graph, evidence existence in cluster/tools, confidence bounds, impact factor re-calculation (flagging $>3$ point variance), sensitive site reflections, and department sequence.
  - Generates `reflection = {"verdict": "approved" | "revised" | "unresolved", "iterations": int, "issues": [...], "checks": [...]}`.
  - Provides a single feedback-driven revision pass if verdict is `"revise"`.
  - Works in deterministic mode with pure rule-based checks.

### Phase 3: Targeted Agent Autonomy (Task 3)
- **Incident Detection (`agents/incident.py`):** Adaptive secondary tool call (distance/historical check) when classification is `POSSIBLE_CONNECTED` with low confidence.
- **Verification Agent (`agents/verification.py`):** When evidence is ambiguous, returns `AWAITING_RESOLUTION_EVIDENCE` with structured `requested_evidence` recommendations. Strict $\le 100\text{m}$ pass, $> 100\text{m}$ fail threshold enforcement.

### Phase 4: Frontend Behavior Visualization (Task 4)
- **New Component:** `frontend/src/components/ToolTraceCard.tsx` (collapsible timeline of model and tool actions with latencies and arguments).
- **Component Updates:**
  - `RootCauseCard.tsx`: Display true `reasoning_mode` badge (3 states), reflection verdict, iterations, and check results.
  - Badges reflect only tools actually executed in `agent_trace`.
  - Type-safe compilation with `npm run build`.

### Phase 5: Evaluation Harness & Ablations (Task 5)
- **New Directory:** `backend/eval/`
  - `eval/cases.json`: 20 labeled test cases (cascades, duplicates, hard negatives, school hazards, cosmetic reports, recurring failures).
  - `eval/run_eval.py`: Quantitative benchmark runner measuring Root Cause Accuracy, Jaccard Chain Match, Priority Accuracy/MAE, Topological Order Violations, Classification Accuracy, and Latencies across modes.
  - `eval/RESULTS.md` & `eval/results.json`: Measurable ablation reports with fixed random seeds.

### Phase 6: Failure Modes, Ambiguous Scenario & Dev Hygiene (Tasks 6 & 7)
- `SIMULATE_TOOL_FAILURE=weather|osm|all` environment flag testing graceful tool degradation.
- Scenario 5: Ambiguous Co-located Reports in `backend/data/scenarios.json`.
- Gate dev endpoints behind `ENABLE_DEV_ENDPOINTS`.
- Documentation updates (`PROMPT.md`, `ARCHITECTURE.md`, `TRD.md`, `FEATURES.md`, `README.md`, `docs/AGENTIC_DESIGN.md`).

---

## 4. Risk Assessment & Mitigations

| Risk | Mitigation |
| :--- | :--- |
| LLM function-calling schema variance across providers | Centralized canonical schema with dedicated adapter functions in `tool_loop.py`. |
| Upstream rate-limiting on OSM Overpass | Retain in-memory cache and 1.0s exponential backoff retry. |
| Endless revision loop in Critic | Strictly bounded at `MAX_REVISIONS = 1` (max 2 total drafts). Fallback to best draft with lowered confidence. |
| Regressions in deterministic offline demo | Scripted unit tests verify deterministic output invariance against all 4 baseline scenarios. |
