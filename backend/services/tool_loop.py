"""
OmniCivic AI -- Provider-Agnostic Agentic Tool Loop

Defines canonical schema for the 5 civic intelligence tools:
- get_weather_forecast
- find_nearby_sensitive_sites
- query_dependency_graph
- get_historical_incidents
- compute_distance

Provides adapters for:
- Anthropic (tool_use / input_schema)
- OpenAI / Groq / OpenRouter / Ollama (tools / function)
- Google Gemini (function_declarations)

Executes an autonomous multi-turn tool calling loop where the model decides
which tools to call and in what order, collecting structured telemetry in agent_trace.
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Callable

import httpx

from services.external_tools import (
    get_weather_forecast,
    find_nearby_sensitive_sites,
    query_dependency_graph,
    get_historical_incidents,
    compute_distance,
)

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

def _now_ist_str() -> str:
    return datetime.now(IST).isoformat()

# ─────────────────────────────────────────────────────────────────────────────
# Canonical Tool Schema Definitions
# ─────────────────────────────────────────────────────────────────────────────

CANONICAL_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "get_weather_forecast",
        "description": "Get hourly rain and precipitation probability forecast for a location over the next 48 hours via Open-Meteo. Use for waterlogging, drainage, or weather-sensitive cascades.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Latitude of the incident location."},
                "longitude": {"type": "number", "description": "Longitude of the incident location."}
            },
            "required": ["latitude", "longitude"]
        }
    },
    {
        "name": "find_nearby_sensitive_sites",
        "description": "Find schools, hospitals, clinics, and kindergartens within radius (meters) using OpenStreetMap Overpass.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Latitude of the incident location."},
                "longitude": {"type": "number", "description": "Longitude of the incident location."},
                "radius_m": {"type": "integer", "description": "Search radius in meters (default 250).", "default": 250}
            },
            "required": ["latitude", "longitude"]
        }
    },
    {
        "name": "query_dependency_graph",
        "description": "Query the civic dependency graph for known causal relationships, typical cascades, and responsible departments for an issue type.",
        "parameters": {
            "type": "object",
            "properties": {
                "issue_type": {"type": "string", "description": "Issue type string, e.g. WATER_PIPE_BURST, POTHOLE, WATERLOGGING, ROAD_CAVE_IN."}
            },
            "required": ["issue_type"]
        }
    },
    {
        "name": "get_historical_incidents",
        "description": "Check whether this location has had prior civic incidents or repeat infrastructure failures from the municipal database.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Latitude of the incident location."},
                "longitude": {"type": "number", "description": "Longitude of the incident location."},
                "radius_m": {"type": "integer", "description": "Radius in meters (default 180).", "default": 180}
            },
            "required": ["latitude", "longitude"]
        }
    },
    {
        "name": "compute_distance",
        "description": "Compute Haversine distance in meters and kilometers between two coordinate pairs.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat1": {"type": "number", "description": "Latitude of point 1."},
                "lon1": {"type": "number", "description": "Longitude of point 1."},
                "lat2": {"type": "number", "description": "Latitude of point 2."},
                "lon2": {"type": "number", "description": "Longitude of point 2."}
            },
            "required": ["lat1", "lon1", "lat2", "lon2"]
        }
    }
]


# ─────────────────────────────────────────────────────────────────────────────
# Provider Adapters
# ─────────────────────────────────────────────────────────────────────────────

def get_anthropic_tools() -> List[Dict[str, Any]]:
    """Convert canonical tools to Anthropic format."""
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "input_schema": t["parameters"]
        }
        for t in CANONICAL_TOOLS
    ]


def get_openai_tools() -> List[Dict[str, Any]]:
    """Convert canonical tools to OpenAI / Groq / OpenRouter / Ollama function-calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"]
            }
        }
        for t in CANONICAL_TOOLS
    ]


def get_gemini_tools() -> List[Dict[str, Any]]:
    """Convert canonical tools to Google Gemini function declaration format."""
    declarations = []
    for t in CANONICAL_TOOLS:
        declarations.append({
            "name": t["name"],
            "description": t["description"],
            "parameters": t["parameters"]
        })
    return [{"function_declarations": declarations}]


# ─────────────────────────────────────────────────────────────────────────────
# Tool Execution Dispatcher
# ─────────────────────────────────────────────────────────────────────────────

async def execute_canonical_tool(tool_name: str, arguments: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Execute a tool call safely, returning (result_dict, error_string).
    """
    try:
        if tool_name == "get_weather_forecast":
            if "latitude" not in arguments or "longitude" not in arguments:
                return {"error": "Missing required arguments latitude, longitude", "available": False}, "Missing required arguments latitude, longitude"
            lat = float(arguments["latitude"])
            lon = float(arguments["longitude"])
            res = await get_weather_forecast(lat, lon)
            err = res.get("reason") if not res.get("available", True) else None
            return res, err

        elif tool_name == "find_nearby_sensitive_sites":
            if "latitude" not in arguments or "longitude" not in arguments:
                return {"error": "Missing required arguments latitude, longitude", "available": False}, "Missing required arguments latitude, longitude"
            lat = float(arguments["latitude"])
            lon = float(arguments["longitude"])
            radius = int(arguments.get("radius_m", 250))
            res = await find_nearby_sensitive_sites(lat, lon, radius)
            err = res.get("reason") if not res.get("available", True) else None
            return res, err

        elif tool_name == "query_dependency_graph":
            if "issue_type" not in arguments:
                return {"error": "Missing required argument issue_type", "available": False}, "Missing required argument issue_type"
            issue_type = str(arguments["issue_type"])
            res = query_dependency_graph(issue_type)
            err = res.get("error") if not res.get("available", True) else None
            return res, err

        elif tool_name == "get_historical_incidents":
            if "latitude" not in arguments or "longitude" not in arguments:
                return {"error": "Missing required arguments latitude, longitude", "available": False}, "Missing required arguments latitude, longitude"
            lat = float(arguments["latitude"])
            lon = float(arguments["longitude"])
            radius = int(arguments.get("radius_m", 180))
            res = get_historical_incidents(lat, lon, radius)
            err = res.get("error") if not res.get("available", True) else None
            return res, err

        elif tool_name == "compute_distance":
            if not all(k in arguments for k in ("lat1", "lon1", "lat2", "lon2")):
                return {"error": "Missing required arguments lat1, lon1, lat2, lon2", "available": False}, "Missing required arguments lat1, lon1, lat2, lon2"
            lat1 = float(arguments["lat1"])
            lon1 = float(arguments["lon1"])
            lat2 = float(arguments["lat2"])
            lon2 = float(arguments["lon2"])
            res = compute_distance(lat1, lon1, lat2, lon2)
            return res, None

        else:
            return {"error": f"Unknown tool '{tool_name}'"}, f"Unknown tool '{tool_name}'"

    except Exception as e:
        logger.warning(f"[TOOL_LOOP] Error executing tool {tool_name} with args {arguments}: {e}")
        return {"error": str(e), "available": False}, str(e)


def _summarize_result(result: Dict[str, Any], max_len: int = 150) -> str:
    """Create a concise summary string for trace logs."""
    if not isinstance(result, dict):
        s = str(result)
        return s[:max_len] + "..." if len(s) > max_len else s

    if "summary" in result:
        return str(result["summary"])[:max_len]
    if "error" in result:
        return f"Error: {result['error']}"[:max_len]
    if "typical_cascade" in result:
        return f"Cascade: {result.get('typical_cascade', [])} (dept: {result.get('primary_department')})"[:max_len]
    if "sites" in result:
        return f"Found {len(result['sites'])} sensitive site(s)"[:max_len]
    if "rain_risk_pct" in result:
        return f"Rain risk: {result.get('rain_risk_pct')}% ({result.get('max_precipitation_mm')}mm)"[:max_len]
    if "distance_m" in result:
        return f"Distance: {result.get('distance_m')}m"[:max_len]

    s = json.dumps(result)
    return s[:max_len] + "..." if len(s) > max_len else s


# ─────────────────────────────────────────────────────────────────────────────
# Unified Multi-Turn Tool Loop
# ─────────────────────────────────────────────────────────────────────────────

async def run_agentic_tool_loop(
    provider: str,
    api_key: str,
    model: str,
    system_prompt: str,
    cluster_summary: Dict[str, Any],
    base_url: str = "",
    max_iterations: int = 6,
    total_timeout: float = 8.0,
    custom_caller: Optional[Callable] = None,
) -> Optional[Dict[str, Any]]:
    """
    Executes an autonomous multi-turn tool-calling loop.
    Returns a dictionary with parsed output, agent_trace, and tools_used,
    or None if loop fails or exceeds timeout.
    """
    provider = provider.lower().strip()
    start_time = time.time()
    step_num = 1
    agent_trace: List[Dict[str, Any]] = []
    tools_used: List[str] = []
    nearby_sites: List[Dict[str, Any]] = []

    user_prompt = (
        f"Investigate this civic complaint cluster using your tools and produce the "
        f"required JSON output with keys: root_cause, impact_score, response_plan.\n\n"
        f"Complaint Cluster:\n{json.dumps(cluster_summary, indent=2)}\n\n"
        f"Return ONLY valid JSON. No conversational preamble or code markdown fences."
    )

    # Prepare provider-specific message state
    openai_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    anthropic_messages = [
        {"role": "user", "content": user_prompt}
    ]
    gemini_contents = [
        {"role": "user", "parts": [{"text": user_prompt}]}
    ]

    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        elapsed = time.time() - start_time
        if elapsed >= total_timeout:
            logger.warning(f"[TOOL_LOOP] Total timeout reached ({elapsed:.2f}s >= {total_timeout}s)")
            break

        remaining_time = max(0.5, total_timeout - elapsed)

        # ── Call Model ──
        call_start = time.time()
        call_error: Optional[str] = None
        assistant_text: Optional[str] = None
        tool_calls: List[Dict[str, Any]] = []

        try:
            if custom_caller:
                # Used in unit tests
                call_res = await custom_caller(
                    messages=openai_messages,
                    tools=CANONICAL_TOOLS,
                    iteration=iteration
                )
                assistant_text = call_res.get("text")
                tool_calls = call_res.get("tool_calls", [])

            elif provider in ["openai", "groq", "openrouter", "ollama", "custom"]:
                endpoint = (
                    "https://api.groq.com/openai/v1/chat/completions" if provider == "groq"
                    else "https://openrouter.ai/api/v1/chat/completions" if provider == "openrouter"
                    else (base_url.rstrip("/") + "/chat/completions" if base_url else "http://localhost:11434/v1/chat/completions") if provider in ["ollama", "custom"]
                    else "https://api.openai.com/v1/chat/completions"
                )
                headers = {"Content-Type": "application/json"}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                if provider == "openrouter":
                    headers["HTTP-Referer"] = "https://omnicivic.ai"
                    headers["X-Title"] = "OmniCivic AI"

                payload = {
                    "model": model,
                    "messages": openai_messages,
                    "tools": get_openai_tools(),
                    "tool_choice": "auto",
                    "temperature": 0.2,
                }

                async with httpx.AsyncClient(timeout=min(remaining_time, 6.0)) as client:
                    resp = await client.post(endpoint, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    choice_msg = data["choices"][0]["message"]
                    assistant_text = choice_msg.get("content")
                    raw_tc = choice_msg.get("tool_calls") or []
                    for rtc in raw_tc:
                        fn = rtc.get("function", {})
                        fn_args = {}
                        try:
                            fn_args = json.loads(fn.get("arguments", "{}"))
                        except Exception:
                            fn_args = {}
                        tool_calls.append({
                            "id": rtc.get("id", f"call_{len(tool_calls)}"),
                            "name": fn.get("name", ""),
                            "arguments": fn_args,
                            "raw_message": choice_msg
                        })

            elif provider in ["claude", "anthropic"]:
                endpoint = "https://api.anthropic.com/v1/messages"
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model or "claude-3-5-sonnet-20241022",
                    "system": system_prompt,
                    "messages": anthropic_messages,
                    "tools": get_anthropic_tools(),
                    "max_tokens": 2048,
                    "temperature": 0.2,
                }

                async with httpx.AsyncClient(timeout=min(remaining_time, 6.0)) as client:
                    resp = await client.post(endpoint, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    content_blocks = data.get("content", [])
                    for b in content_blocks:
                        if b.get("type") == "text":
                            assistant_text = (assistant_text or "") + b.get("text", "")
                        elif b.get("type") == "tool_use":
                            tool_calls.append({
                                "id": b.get("id"),
                                "name": b.get("name"),
                                "arguments": b.get("input", {}),
                                "content_block": b
                            })

            elif provider == "gemini":
                clean_model = (model or "gemini-2.0-flash").replace("models/", "")
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": gemini_contents,
                    "tools": get_gemini_tools(),
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                }

                async with httpx.AsyncClient(timeout=min(remaining_time, 6.0)) as client:
                    resp = await client.post(endpoint, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for p in parts:
                            if "text" in p:
                                assistant_text = (assistant_text or "") + p["text"]
                            elif "functionCall" in p:
                                fc = p["functionCall"]
                                tool_calls.append({
                                    "id": f"call_{len(tool_calls)}",
                                    "name": fc.get("name"),
                                    "arguments": fc.get("args", {}),
                                    "raw_part": p
                                })
            else:
                logger.warning(f"[TOOL_LOOP] Provider {provider} not supported for native agentic loop.")
                return None

        except Exception as e:
            call_error = str(e)
            logger.warning(f"[TOOL_LOOP] Model call iteration {iteration} error: {e}")

        call_latency = round((time.time() - call_start) * 1000, 1)

        # Record model call in trace
        agent_trace.append({
            "step": step_num,
            "type": "model_call",
            "tool_name": None,
            "arguments": None,
            "result_summary": f"Iteration {iteration} completed ({len(tool_calls)} tool calls requested)",
            "latency_ms": call_latency,
            "error": call_error,
            "timestamp": _now_ist_str(),
        })
        step_num += 1

        if call_error:
            # If model invocation failed, break loop
            break

        # If no tool calls were requested, model provided final answer
        if not tool_calls:
            clean_text = (assistant_text or "").strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            parsed: Optional[Dict[str, Any]] = None
            try:
                parsed = json.loads(clean_text.strip())
            except Exception as pe:
                logger.warning(f"[TOOL_LOOP] JSON parse error on final text: {pe}")

            agent_trace.append({
                "step": step_num,
                "type": "final",
                "tool_name": None,
                "arguments": None,
                "result_summary": clean_text[:120] if parsed else "Failed to parse final JSON",
                "latency_ms": 0.0,
                "error": None if parsed else "Invalid JSON in final completion",
                "timestamp": _now_ist_str(),
            })
            step_num += 1

            if parsed:
                # Attach tool traces and sites to output
                if "root_cause" in parsed:
                    parsed["root_cause"]["nearby_sites"] = nearby_sites
                parsed["nearby_sites"] = nearby_sites
                parsed["reasoning_mode"] = "agentic_multi_turn"
                parsed["tools_used"] = list(set(tools_used))
                parsed["agent_trace"] = agent_trace
                return parsed
            else:
                break

        # ── Execute Tool Calls ──
        # Update messages for tool feedback
        if provider in ["openai", "groq", "openrouter", "ollama", "custom"]:
            raw_msg = tool_calls[0].get("raw_message", {})
            openai_messages.append({
                "role": "assistant",
                "content": assistant_text,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"])
                        }
                    }
                    for tc in tool_calls
                ]
            })

        elif provider in ["claude", "anthropic"]:
            anthropic_content = []
            if assistant_text:
                anthropic_content.append({"type": "text", "text": assistant_text})
            for tc in tool_calls:
                anthropic_content.append(tc.get("content_block", {
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["arguments"]
                }))
            anthropic_messages.append({"role": "assistant", "content": anthropic_content})

        claude_tool_results = []
        gemini_responses = []

        for tc in tool_calls:
            t_name = tc["name"]
            t_args = tc["arguments"]
            tools_used.append(t_name)

            # Record tool call step
            agent_trace.append({
                "step": step_num,
                "type": "tool_call",
                "tool_name": t_name,
                "arguments": t_args,
                "result_summary": f"Calling tool {t_name}",
                "latency_ms": 0.0,
                "error": None,
                "timestamp": _now_ist_str(),
            })
            step_num += 1

            # Execute tool
            t_start = time.time()
            t_res, t_err = await execute_canonical_tool(t_name, t_args)
            t_latency = round((time.time() - t_start) * 1000, 1)

            if t_name == "find_nearby_sensitive_sites" and t_res.get("available"):
                nearby_sites.extend(t_res.get("sites", []))

            res_summary = _summarize_result(t_res)

            # Record tool result step
            agent_trace.append({
                "step": step_num,
                "type": "tool_result",
                "tool_name": t_name,
                "arguments": None,
                "result_summary": res_summary,
                "latency_ms": t_latency,
                "error": t_err,
                "timestamp": _now_ist_str(),
            })
            step_num += 1

            # Append to message history
            if provider in ["openai", "groq", "openrouter", "ollama", "custom"]:
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": t_name,
                    "content": json.dumps(t_res)
                })
            elif provider in ["claude", "anthropic"]:
                claude_tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc["id"],
                    "content": json.dumps(t_res)
                })
            elif provider == "gemini":
                gemini_responses.append({
                    "functionResponse": {
                        "name": t_name,
                        "response": {"name": t_name, "content": t_res}
                    }
                })

        if provider in ["claude", "anthropic"] and claude_tool_results:
            anthropic_messages.append({"role": "user", "content": claude_tool_results})
        elif provider == "gemini" and gemini_responses:
            gemini_contents.append({"role": "user", "parts": gemini_responses})

    logger.warning(f"[TOOL_LOOP] Loop exited without final valid JSON after {iteration} iterations.")
    return None
