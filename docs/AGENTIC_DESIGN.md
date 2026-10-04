# OmniCivic AI — Agentic Design, Autonomous Boundaries & Evaluation

This document outlines the architectural boundary between **Autonomous Agentic Intelligence** and **Deterministic Engineering** in OmniCivic AI, detailing design trade-offs, reflection mechanisms, and empirical evaluation results.

---

## 1. What is Genuinely Agentic vs Deterministic by Design

A common failure mode in civic and AI systems is "agent-washing"—labeling procedural scripts, hardcoded templates, or single-shot prompts as "autonomous agents." OmniCivic AI maintains a rigorous and transparent line:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           OmniCivic System Spectrum                             │
├───────────────────────────────────────┬─────────────────────────────────────────┤
│         Genuinely Agentic             │         Deterministic by Design         │
├───────────────────────────────────────┼─────────────────────────────────────────┤
│ • Dynamic, un-prompted tool selection │ • Geographic clustering (Haversine math)│
│ • Multi-turn observation-action loop  │ • 100m spatial pass/fail threshold     │
│ • Self-critique & revision pass       │ • Topological sort over municipal DAG   │
│ • Adaptive clarification / evidence   │ • Fernet 256-bit encryption at rest     │
│ • Graceful degradation across models  │ • SLA countdown & state transition clock│
└───────────────────────────────────────┴─────────────────────────────────────────┘
```

### A. What is Genuinely Agentic

1. **Autonomous Tool Selection & Calling Loop (`backend/services/tool_loop.py`):**
   - The LLM receives raw cluster reports and a tool catalog of 5 external tools (`get_weather_forecast`, `find_nearby_sensitive_sites`, `query_dependency_graph`, `get_historical_incidents`, `compute_distance`).
   - The model autonomously determines **if**, **which**, and **in what order** to call tools. It is not fed pre-called answers in agentic mode.
   - Operates across all major LLM families (Anthropic Claude, OpenAI, Groq, OpenRouter, Ollama, Gemini) via a canonical schema and format adapters.
   - Halts dynamically upon achieving sufficient epistemic confidence or hitting the iteration budget (max 6 turns).

2. **Self-Critique & Reflection Agent (`backend/agents/critic.py`):**
   - Implements reflection as a distinct cognitive pass. Draft reasoning outputs are audited against 6 verification checks:
     - Knowledge graph edge presence (`civic_dependencies.json`).
     - Grounded evidence fidelity (no hallucinated landmarks).
     - Confidence boundedness relative to evidence density.
     - Mathematical consistency of the impact formula ($0.30/0.20/0.15/0.10/0.10/0.15$) and priority thresholds ($\ge 80$ CRITICAL, 65-79 HIGH, 45-64 MEDIUM, $<45$ LOW).
     - Proximity weighting for sensitive sites $\le 250\text{m}$.
     - Topological feasibility of the multi-department response sequence.
   - If flawed, triggers an autonomous revision pass with specific diagnostics. If issues persist, marks `verdict = "unresolved"` and downgrades confidence.

3. **Adaptive Incident Disambiguation (`backend/agents/incident.py`):**
   - When report cluster relationships are borderline (`POSSIBLE_CONNECTED` with confidence $<0.75$), the agent autonomously triggers a secondary historical search before finalizing its classification.

4. **Adaptive Field Verification (`backend/agents/verification.py`):**
   - If field evidence submitted by contractors is ambiguous or borderline, rather than a naive binary pass/fail, the agent issues an `AWAITING_RESOLUTION_EVIDENCE` status with structured, actionable requirements (e.g. "submit photo within 100m showing street landmark").

---

### B. What is Deterministic by Design (and Why)

Certain civic responsibilities must never be delegated to stochastic LLM generation:

1. **Safety-Critical Geographic Boundaries:**
   - Determining whether a contractor actually visited the repair site uses spherical Haversine math ($d \le 100\text{m}$ passes, $> 100\text{m}$ fails). Allowing an LLM to "estimate" distance invites hallucinated pass verdicts.
2. **Departmental Precedence (Topological Sort):**
   - Paving over an unsealed, ruptured water pipe causes catastrophic sinkholes. The mandatory order (utilities $\to$ drainage $\to$ surface asphalt) is enforced deterministically by directed acyclic graph (DAG) topological sorting.
3. **Data Integrity & Audit Log Invariance:**
   - Only the Orchestrator agent may persist state to `incidents.json` and `agent_logs.json`. LLMs cannot write directly to database files.
4. **Offline Deterministic Fallback Mode:**
   - Municipal emergency infrastructure must continue operating during widespread network outages, power interruptions, or third-party API downtime. In offline mode, graph search and formula evaluation run in $< 10\text{ms}$ with zero network or remote API keys.

---

## 2. Telemetry & Execution Tracing

Every run produces an audit-ready, structured `agent_trace` recording:
- `step`: Turn index (1, 2, 3...)
- `type`: `"model_call"` | `"tool_call"` | `"tool_result"` | `"final"` | `"deterministic"`
- `tool`: Canonical tool name invoked
- `args`: Arguments passed to the tool
- `result_summary`: Truncated, sanitized return payload
- `latency_ms`: Exact millisecond duration of each step
- `error`: Handled exceptions or timeout notes

The active mode is truthfully reported as one of:
- `"agentic_multi_turn"`
- `"single_turn_enriched"`
- `"deterministic_fallback"`

The system never falsely claims `"agentic_multi_turn"` when running on single-turn enrichment or deterministic fallback.

---

## 3. Quantitative Evaluation & Ablation

OmniCivic includes an automated evaluation harness (`backend/eval/`):
- **Benchmark Dataset (`eval/cases.json`):** 20 ground-truth labeled municipal cases, including complex cascades, duplicates, school hazard cases, cosmetic issues, and hard negatives (unrelated co-located reports).
- **Harness Runner (`eval/run_eval.py`):** Evaluates modes offline via:
  ```bash
  python -m eval.run_eval --mode deterministic
  ```
- **Evaluation Output (`eval/RESULTS.md`):** Generates reproducible metrics covering:
  - Root Cause Accuracy
  - Causal Chain Exact Match & Jaccard Index
  - Priority Classification Accuracy & Mean Absolute Error (MAE)
  - Department Topological Feasibility (0% inversions guaranteed)
  - Hard Negative False-Connection Rate (0.0% false merges on Ambiguous Co-Located reports)
  - Latency & Tool Call Efficiency

---

## 4. Current Limitations & Future Work

1. **Local Vision Latency:** In deterministic offline mode, perception relies on visual lookup tables or lightweight heuristics; deploying an on-premise quantized vision model (e.g. Moondream or LLaVA-mini) would provide fully offline multimodal understanding.
2. **Dynamic DAG Evolution:** The civic dependency graph (`civic_dependencies.json`) is currently human-curated. Future iterations could allow the Critic agent to propose new candidate edges to human municipal engineers based on multi-month incident data.
3. **Real-Time Sensor Telemetry:** Integrating SCADA water pressure sensors and smart electric meters directly into the tool loop would allow the agent to verify physical pressure drops alongside citizen complaints.
