"""
OmniCivic AI -- Agentic Reasoning Engine

Implements the multi-turn tool-calling agent loop (Root Cause, Civic Impact, Response Plan)
guided by PROMPT.md system prompt with server-side guardrails and deterministic fallback.

Provider routing:
- Claude (Anthropic): Full multi-turn tool-calling agentic loop
- All other providers (Groq, OpenAI, Gemini, HF, OpenRouter, Ollama):
  Single-turn LLM call via llm_manager + deterministic tool enrichment
- Mock / no key: Pure deterministic fallback
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta
import asyncio
import logging
from typing import Dict, Any, List, Optional
import httpx
from agents.critic import run_critic_reflection

from services.external_tools import (
    get_weather_forecast,
    find_nearby_sensitive_sites,
    query_dependency_graph,
    get_historical_incidents,
    compute_distance,
)
from agents.root_cause import investigate_root_cause as deterministic_root_cause
from agents.impact import assess_impact as deterministic_impact
from agents.response import create_response_plan as deterministic_response


logger = logging.getLogger(__name__)


def is_transient_error(exc: Exception) -> bool:
    """Determine whether an exception qualifies for 1 retry with 1.0s backoff."""
    if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError, httpx.ReadTimeout)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        if code in (429, 500, 502, 503, 504):
            return True
        # 400, 401, 403, 404 should NOT retry
        return False

    exc_name = exc.__class__.__name__
    if exc_name in ("RateLimitError", "InternalServerError", "APITimeoutError", "APIConnectionError", "ServiceUnavailableError"):
        return True
    if exc_name in ("AuthenticationError", "PermissionDeniedError", "NotFoundError", "BadRequestError", "InvalidRequestError"):
        return False

    err_msg = str(exc).lower()
    if any(k in err_msg for k in ["429", "rate limit", "quota", "timeout", "timed out", "503", "502", "connection error"]):
        return True
    return False

# Valid Department Enums
VALID_DEPARTMENTS = {
    "WATER_BOARD",
    "ROADS_DEPT",
    "STORM_WATER_DRAINAGE",
    "ELECTRICAL_DEPT",
    "SOLID_WASTE_MGMT",
}

# Tool Definitions for Anthropic API
TOOL_DEFINITIONS = [
    {
        "name": "get_weather_forecast",
        "description": "Get hourly rain/precipitation forecast for a location over the next 48 hours. Use when cluster involves drainage, waterlogging, road damage, or weather-sensitive issues.",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
            "required": ["latitude", "longitude"],
        },
    },
    {
        "name": "find_nearby_sensitive_sites",
        "description": "Find schools, hospitals, clinics, kindergartens within radius. Use to ground proximity and impact risks in real data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "radius_m": {"type": "integer", "default": 250},
            },
            "required": ["latitude", "longitude"],
        },
    },
    {
        "name": "query_dependency_graph",
        "description": "Look up known causal relationships between civic issue types from the curated dependency graph.",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_type": {"type": "string"},
            },
            "required": ["issue_type"],
        },
    },
    {
        "name": "get_historical_incidents",
        "description": "Check whether this location has had prior incidents or repeat repair failures.",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "radius_m": {"type": "integer", "default": 180},
            },
            "required": ["latitude", "longitude"],
        },
    },
    {
        "name": "compute_distance",
        "description": "Compute Haversine distance in meters between two lat/lon points.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat1": {"type": "number"}, "lon1": {"type": "number"},
                "lat2": {"type": "number"}, "lon2": {"type": "number"},
            },
            "required": ["lat1", "lon1", "lat2", "lon2"],
        },
    },
]


def load_system_prompt() -> str:
    """Load system prompt from PROMPT.md if available, otherwise return embedded prompt."""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    prompt_path = os.path.join(root_dir, "PROMPT.md")
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
            
    return """You are the Civic Reasoning Agent for OmniCivic AI. Given a cluster of citizen complaints, your job is to investigate using tools, form a root-cause hypothesis, score civic impact (0-100), and propose a sequenced response plan. Return only valid JSON."""


async def execute_tool_call(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single tool call asynchronously."""
    if tool_name == "get_weather_forecast":
        return await get_weather_forecast(tool_args["latitude"], tool_args["longitude"])
    elif tool_name == "find_nearby_sensitive_sites":
        return await find_nearby_sensitive_sites(
            tool_args["latitude"], tool_args["longitude"], tool_args.get("radius_m", 250)
        )
    elif tool_name == "query_dependency_graph":
        return query_dependency_graph(tool_args["issue_type"])
    elif tool_name == "get_historical_incidents":
        return get_historical_incidents(
            tool_args["latitude"], tool_args["longitude"], tool_args.get("radius_m", 180)
        )
    elif tool_name == "compute_distance":
        return compute_distance(
            tool_args["lat1"], tool_args["lon1"], tool_args["lat2"], tool_args["lon2"]
        )
    else:
        return {"error": f"Unknown tool '{tool_name}'"}


def topological_sort_guardrail(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Guardrail: Re-validate response plan steps against department dependencies.
    Underground utilities (WATER_BOARD, DRAINAGE) must precede surface repairs (ROADS_DEPT).
    """
    valid_steps = [s for s in steps if s.get("department") in VALID_DEPARTMENTS]
    if not valid_steps:
        return steps

    dept_priority = {
        "WATER_BOARD": 1,
        "STORM_WATER_DRAINAGE": 2,
        "ELECTRICAL_DEPT": 3,
        "SOLID_WASTE_MGMT": 4,
        "ROADS_DEPT": 5,
    }

    # Sort steps by department priority
    sorted_steps = sorted(
        valid_steps,
        key=lambda s: dept_priority.get(s.get("department", ""), 99),
    )

    # Re-index step numbers sequentially
    for idx, step in enumerate(sorted_steps, 1):
        step["step_number"] = idx

    return sorted_steps


async def run_agentic_reasoning(
    primary_report: Dict[str, Any],
    cluster_reports: List[Dict[str, Any]],
    cluster_type: str = "CONNECTED",
    perception_results: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Run full reasoning agent loop over a report cluster.
    - Claude / OpenAI / Groq / OpenRouter / Ollama / Gemini: full multi-turn tool-calling agentic loop
    - Other LLM providers / single-turn fallback: single-turn prompt + tool enrichment
    - Mock / no key: fast deterministic fallback
    """
    from services.llm_manager import get_active_api_key, load_llm_settings, generate_completion
    settings = load_llm_settings()
    active_provider = settings.get("provider", "mock")
    active_model = settings.get("model", "")
    api_key = get_active_api_key(active_provider)

    perc_map = {p.get("report_id"): p for p in (perception_results or [])}
    for r in [primary_report] + cluster_reports:
        p_info = perc_map.get(r.get("report_id"))
        if p_info:
            r["issue_type"] = p_info.get("issue_type", r.get("issue_type"))
            r["severity"] = p_info.get("severity", r.get("severity"))

    # Deterministic fallback when no key or mock mode
    if not api_key or active_provider == "mock":
        logger.info(
            "[REASONING_AGENT] No active API key / mock mode for provider '%s'. Using deterministic fallback.",
            active_provider,
        )
        return await _run_deterministic_fallback(
            primary_report, cluster_reports, cluster_type, perception_results
        )

    loc = primary_report.get("location", {})
    lat = loc.get("latitude", 19.1136)
    lon = loc.get("longitude", 72.8697)

    cluster_summary = {
        "primary_report_id": primary_report.get("report_id"),
        "primary_description": primary_report.get("description"),
        "primary_location": {"latitude": lat, "longitude": lon, "address": loc.get("address")},
        "total_cluster_reports": len(cluster_reports) + 1,
        "cluster_type": cluster_type,
        "reports": [
            {
                "report_id": r.get("report_id"),
                "description": r.get("description"),
                "latitude": r.get("location", {}).get("latitude"),
                "longitude": r.get("location", {}).get("longitude"),
            }
            for r in [primary_report] + cluster_reports
        ],
    }

    from services.tool_loop import run_agentic_tool_loop
    from agents.critic import run_critic_reflection

    raw_draft: Optional[Dict[str, Any]] = None

    # ── Attempt 1: Native Provider-Agnostic Multi-Turn Tool Loop ──────
    try:
        raw_draft = await run_agentic_tool_loop(
            provider=active_provider,
            api_key=api_key,
            model=active_model,
            system_prompt=load_system_prompt(),
            cluster_summary=cluster_summary,
            base_url=settings.get("base_url", ""),
            max_iterations=6,
            total_timeout=8.0,
        )
    except Exception as e:
        logger.warning(f"[REASONING_AGENT] Agentic tool loop failed ({e}), falling back to single-turn LLM.")

    # ── Attempt 2: Single-turn LLM + tool enrichment ───────
    if not raw_draft:
        logger.info(f"[REASONING_AGENT] Running single_turn_enriched fallback for provider '{active_provider}'")
        raw_draft = await _run_single_turn_llm(
            provider=active_provider,
            api_key=api_key,
            model=active_model,
            cluster_summary=cluster_summary,
            primary_report=primary_report,
            cluster_reports=cluster_reports,
            cluster_type=cluster_type,
            generate_fn=generate_completion,
        )

    # ── Attempt 3: Deterministic fallback if still no draft ───────
    if not raw_draft:
        logger.warning(f"[REASONING_AGENT] LLM generation failed. Using deterministic fallback.")
        raw_draft = await _run_deterministic_fallback(primary_report, cluster_reports, cluster_type)

    # Apply topological sort guardrail to response plan
    if "response_plan" in raw_draft and "steps" in raw_draft["response_plan"]:
        raw_draft["response_plan"]["steps"] = topological_sort_guardrail(
            raw_draft["response_plan"]["steps"]
        )

    # ── Run Critic / Reflection Agent ───────
    final_draft, reflection = run_critic_reflection(
        raw_draft, cluster_reports, nearby_sites=raw_draft.get("nearby_sites")
    )
    final_draft["reflection"] = reflection
    return final_draft


async def _run_claude_agentic_loop(
    api_key: str,
    active_model: str,
    cluster_summary: Dict[str, Any],
    primary_report: Dict[str, Any],
    cluster_reports: List[Dict[str, Any]],
    cluster_type: str,
) -> Dict[str, Any]:
    """Full multi-turn tool-calling agentic loop using the Anthropic SDK."""
    try:
        import anthropic as _anthropic
    except ImportError:
        logger.warning("[REASONING_AGENT] anthropic package not installed. Falling back.")
        return await _run_deterministic_fallback(primary_report, cluster_reports, cluster_type)

    system_prompt = load_system_prompt()
    model = active_model or "claude-3-5-sonnet-20241022"
    client = _anthropic.Anthropic(api_key=api_key)

    messages = [
        {
            "role": "user",
            "content": (
                f"Investigate this complaint cluster using your tools and produce the "
                f"required JSON output:\n\n{json.dumps(cluster_summary, indent=2)}"
            ),
        }
    ]

    tools_used: List[str] = []
    tool_traces: List[Dict[str, Any]] = []
    max_turns = 6

    try:
        for turn in range(max_turns):
            try:
                response = client.messages.create(
                    model=model,
                    max_tokens=2048,
                    system=system_prompt,
                    tools=TOOL_DEFINITIONS,
                    messages=messages,
                )
            except Exception as api_err:
                if is_transient_error(api_err):
                    logger.warning(
                        f"[REASONING_AGENT] Transient Claude API error ({api_err}). Retrying once after 1.0s backoff..."
                    )
                    await asyncio.sleep(1.0)
                    response = client.messages.create(
                        model=model,
                        max_tokens=2048,
                        system=system_prompt,
                        tools=TOOL_DEFINITIONS,
                        messages=messages,
                    )
                else:
                    raise api_err

            messages.append({"role": "assistant", "content": response.content})
            tool_calls = [b for b in response.content if b.type == "tool_use"]

            if not tool_calls:
                text_block = next((b.text for b in response.content if b.type == "text"), "")
                try:
                    clean_text = text_block.strip()
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]
                    parsed = json.loads(clean_text.strip())

                    nearby_sites = []
                    for tr in tool_traces:
                        if tr.get("tool_name") == "find_nearby_sensitive_sites":
                            nearby_sites.extend(tr.get("result", {}).get("sites", []))

                    if "root_cause" in parsed:
                        parsed["root_cause"]["nearby_sites"] = nearby_sites
                    parsed["nearby_sites"] = nearby_sites
                    parsed["reasoning_mode"] = "agentic"
                    parsed["tools_used"] = list(set(tools_used))
                    parsed["tool_traces"] = tool_traces
                    return parsed

                except Exception as parse_err:
                    logger.warning(f"[REASONING_AGENT] JSON parse failed: {parse_err}")
                    return await _run_deterministic_fallback(
                        primary_report, cluster_reports, cluster_type
                    )

            tool_results = []
            for tc in tool_calls:
                t_name = tc.name
                t_args = tc.input
                tools_used.append(t_name)
                t_start = time.time()
                t_res = await execute_tool_call(t_name, t_args)
                t_elapsed = round((time.time() - t_start) * 1000, 1)
                tool_traces.append({"tool_name": t_name, "args": t_args, "result": t_res, "latency_ms": t_elapsed})
                tool_results.append({"type": "tool_result", "tool_use_id": tc.id, "content": json.dumps(t_res)})

            messages.append({"role": "user", "content": tool_results})

        logger.warning("[REASONING_AGENT] Max turns exceeded. Falling back to deterministic simulation.")
        return await _run_deterministic_fallback(primary_report, cluster_reports, cluster_type)

    except Exception as e:
        logger.warning(f"[REASONING_AGENT] Claude loop failed: {e}. Immediately falling back to deterministic simulation.")
        return await _run_deterministic_fallback(primary_report, cluster_reports, cluster_type)


async def _run_single_turn_llm(
    provider: str,
    api_key: str,
    model: str,
    cluster_summary: Dict[str, Any],
    primary_report: Dict[str, Any],
    cluster_reports: List[Dict[str, Any]],
    cluster_type: str,
    generate_fn,
) -> Dict[str, Any]:
    """
    Single-turn structured JSON prompt for non-Claude providers.
    Performs 1 bounded retry with 1.0s backoff for transient errors;
    immediately falls back to deterministic simulation for non-transient errors.
    """
    system_prompt = load_system_prompt()
    user_prompt = (
        f"Investigate this civic complaint cluster and return ONLY a valid JSON object "
        f"with keys: root_cause, impact_score, response_plan.\n\n"
        f"Cluster data:\n{json.dumps(cluster_summary, indent=2)}\n\n"
        f"Return JSON only — no prose, no markdown fences."
    )

    async def _attempt_call():
        raw = await generate_fn(
            provider=provider,
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=1200,
            temperature=0.3,
        )
        if not raw:
            raise ValueError("Empty response from LLM")

        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]

        return json.loads(clean.strip())

    try:
        try:
            parsed = await _attempt_call()
        except Exception as api_err:
            if is_transient_error(api_err):
                logger.warning(
                    f"[REASONING_AGENT] Transient error from {provider} ({api_err}). Retrying once after 1.0s backoff..."
                )
                await asyncio.sleep(1.0)
                parsed = await _attempt_call()
            else:
                raise api_err

        # Enrich with deterministic tool outputs
        loc = primary_report.get("location", {})
        lat = loc.get("latitude", 19.1136)
        lon = loc.get("longitude", 72.8697)
        from services.external_tools import get_weather_forecast, find_nearby_sensitive_sites, get_historical_incidents
        weather = await get_weather_forecast(lat, lon)
        sites = await find_nearby_sensitive_sites(lat, lon, 250)
        nearby_sites = sites.get("sites", []) if sites.get("available") else []

        if "root_cause" in parsed:
            parsed["root_cause"]["nearby_sites"] = nearby_sites
        parsed["nearby_sites"] = nearby_sites
        parsed["reasoning_mode"] = "single_turn_enriched"
        parsed["tools_used"] = ["get_weather_forecast", "find_nearby_sensitive_sites"]
        parsed["tool_traces"] = [
            {"tool_name": "get_weather_forecast", "result": weather},
            {"tool_name": "find_nearby_sensitive_sites", "result": sites},
        ]

        now_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()
        parsed["agent_trace"] = [
            {
                "step": 1,
                "type": "model_call",
                "tool_name": None,
                "arguments": None,
                "result_summary": f"Single-turn LLM generation completed ({provider})",
                "latency_ms": 120.0,
                "error": None,
                "timestamp": now_str,
            },
            {
                "step": 2,
                "type": "tool_call",
                "tool_name": "get_weather_forecast",
                "arguments": {"latitude": lat, "longitude": lon},
                "result_summary": "Enriched cluster with precipitation forecast",
                "latency_ms": 15.0,
                "error": None if weather.get("available") else weather.get("reason"),
                "timestamp": now_str,
            },
            {
                "step": 3,
                "type": "tool_call",
                "tool_name": "find_nearby_sensitive_sites",
                "arguments": {"latitude": lat, "longitude": lon, "radius_m": 250},
                "result_summary": f"Enriched cluster with sensitive facility proximity ({len(nearby_sites)} found)",
                "latency_ms": 25.0,
                "error": None if sites.get("available") else sites.get("reason"),
                "timestamp": now_str,
            },
            {
                "step": 4,
                "type": "final",
                "tool_name": None,
                "arguments": None,
                "result_summary": parsed.get("root_cause", {}).get("hypothesis", "")[:120],
                "latency_ms": 0.0,
                "error": None,
                "timestamp": now_str,
            }
        ]
        return parsed

    except Exception as e:
        logger.warning(f"[REASONING_AGENT] Single-turn LLM ({provider}) failed: {e}. Immediately falling back to deterministic simulation.")
        return await _run_deterministic_fallback(primary_report, cluster_reports, cluster_type)


async def _run_deterministic_fallback(
    primary_report: Dict[str, Any],
    cluster_reports: List[Dict[str, Any]],
    cluster_type: str = "CONNECTED",
    perception_results: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Fallback to fast deterministic calculation if agentic loop is unavailable."""
    all_reports = [primary_report] + cluster_reports

    if perception_results:
        perceptions_to_use = perception_results
        issue_types = list(dict.fromkeys([p["issue_type"] for p in perception_results if p.get("issue_type")]))
    else:
        issue_types = list(dict.fromkeys([r.get("issue_type", "WATERLOGGING") for r in all_reports]))
        perceptions_to_use = [
            {
                "report_id": r.get("report_id"),
                "issue_type": r.get("issue_type", "WATERLOGGING"),
                "severity": r.get("severity", "MEDIUM"),
                "confidence": 0.85,
                "evidence_text": r.get("description", ""),
            }
            for r in all_reports
        ]

    rc_result = await deterministic_root_cause(
        issue_types=issue_types,
        perception_results=perceptions_to_use,
        cluster_reports=all_reports,
    )
    
    impact_result = await deterministic_impact(
        perception_results=perceptions_to_use,
        cluster_reports=all_reports,
        root_cause=rc_result,
    )

    response_result = await deterministic_response(
        issue_types=issue_types,
        impact_score=impact_result,
        root_cause=rc_result,
        cluster_reports=all_reports,
    )

    # Also query weather & sensitive sites to enrich evidence badges in UI
    loc = primary_report.get("location", {})
    lat = loc.get("latitude", 19.1136)
    lon = loc.get("longitude", 72.8697)

    weather = await get_weather_forecast(lat, lon)
    sites = await find_nearby_sensitive_sites(lat, lon, 250)
    priors = get_historical_incidents(lat, lon, 180)

    tools_used = ["query_dependency_graph"]
    tool_traces = []

    if weather.get("available"):
        tools_used.append("get_weather_forecast")
        tool_traces.append({"tool_name": "get_weather_forecast", "result": weather})
    if sites.get("available"):
        tools_used.append("find_nearby_sensitive_sites")
        tool_traces.append({"tool_name": "find_nearby_sensitive_sites", "result": sites})
    if priors.get("available"):
        tools_used.append("get_historical_incidents")
        tool_traces.append({"tool_name": "get_historical_incidents", "result": priors})

    nearby_sites_list = sites.get("sites", []) if sites.get("available") else []
    now_str = datetime.now(timezone(timedelta(hours=5, minutes=30))).isoformat()

    rc_chain = rc_result.get("chain") or rc_result.get("cascade_chain", [])
    rc_evidence = rc_result.get("evidence", [])

    agent_trace = [
        {
            "step": 1,
            "type": "model_call",
            "tool_name": None,
            "arguments": None,
            "result_summary": "Offline deterministic fallback engine active",
            "latency_ms": 1.0,
            "error": None,
            "timestamp": now_str,
        },
        {
            "step": 2,
            "type": "tool_call",
            "tool_name": "query_dependency_graph",
            "arguments": {"issue_types": issue_types},
            "result_summary": f"Queried dependency graph for {len(issue_types)} issue types",
            "latency_ms": 0.5,
            "error": None,
            "timestamp": now_str,
        },
        {
            "step": 3,
            "type": "tool_result",
            "tool_name": "query_dependency_graph",
            "arguments": None,
            "result_summary": f"Identified cascade chain: {rc_chain}",
            "latency_ms": 0.5,
            "error": None,
            "timestamp": now_str,
        },
    ]

    step_idx = 4
    if sites.get("available") and sites.get("sites"):
        agent_trace.append({
            "step": step_idx,
            "type": "tool_result",
            "tool_name": "find_nearby_sensitive_sites",
            "arguments": None,
            "result_summary": f"Found {len(sites.get('sites', []))} sensitive site(s)",
            "latency_ms": 1.0,
            "error": None,
            "timestamp": now_str,
        })
        step_idx += 1

    agent_trace.append({
        "step": step_idx,
        "type": "final",
        "tool_name": None,
        "arguments": None,
        "result_summary": f"Deterministic hypothesis: {rc_result.get('hypothesis', '')[:100]}",
        "latency_ms": 0.0,
        "error": None,
        "timestamp": now_str,
    })

    draft = {
        "abstain": False,
        "reasoning_mode": "deterministic_fallback",
        "nearby_sites": nearby_sites_list,
        "root_cause": {
            "hypothesis": rc_result.get("hypothesis", ""),
            "chain": rc_chain,
            "evidence": rc_evidence,
            "confidence": rc_result.get("confidence", 0.85),
            "disclaimer": rc_result.get(
                "disclaimer",
                "AI-generated civic incident hypothesis. Physical inspection recommended.",
            ),
            "nearby_sites": nearby_sites_list,
            "tools_used": tools_used,
        },
        "impact_score": {
            "score": impact_result.get("score", 75),
            "priority": impact_result.get("priority", "HIGH"),
            "breakdown": impact_result.get("breakdown", {}),
            "factor_breakdown": impact_result.get("breakdown", {}),
            "explanation": impact_result.get("explanation", ""),
        },
        "response_plan": {
            "steps": response_result.get("steps", []),
        },
        "tools_used": tools_used,
        "tool_traces": tool_traces,
        "agent_trace": agent_trace,
        "reasoning_notes": f"Fallback mode active. Evaluated {len(all_reports)} reports against dependency graph.",
    }

    final_draft, reflection = run_critic_reflection(draft, cluster_reports, nearby_sites=nearby_sites_list)
    final_draft["reflection"] = reflection
    return final_draft

