"""
Unit tests for the Provider-Agnostic Agentic Tool Loop (backend/services/tool_loop.py).

Verifies:
1. Multi-turn autonomous tool selection with a scripted fake caller (no network).
2. Trace generation adhering to schema (step, type, latency, summary).
3. Handling of iteration limit (loop terminates cleanly).
4. Resilience when a tool encounters an error / raises exception.
"""

import asyncio
import json
import pytest
import sys
import os

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.tool_loop import (
    run_agentic_tool_loop,
    get_anthropic_tools,
    get_openai_tools,
    get_gemini_tools,
    CANONICAL_TOOLS,
    execute_canonical_tool,
)


def test_schema_adapters():
    """Verify tool adapters correctly transform the 5 canonical tools."""
    assert len(CANONICAL_TOOLS) == 5

    anthropic_tools = get_anthropic_tools()
    assert len(anthropic_tools) == 5
    for t in anthropic_tools:
        assert "name" in t
        assert "description" in t
        assert "input_schema" in t

    openai_tools = get_openai_tools()
    assert len(openai_tools) == 5
    for t in openai_tools:
        assert t["type"] == "function"
        assert "function" in t
        assert "name" in t["function"]
        assert "parameters" in t["function"]

    gemini_tools = get_gemini_tools()
    assert len(gemini_tools) == 1
    assert "function_declarations" in gemini_tools[0]
    assert len(gemini_tools[0]["function_declarations"]) == 5


@pytest.mark.asyncio
async def test_tool_execution_and_resilience():
    """Verify local execution of canonical tools and handling of bad args/unknown tools."""
    # Haversine distance tool
    res, err = await execute_canonical_tool(
        "compute_distance",
        {"lat1": 19.1136, "lon1": 72.8697, "lat2": 19.1140, "lon2": 72.8700}
    )
    assert err is None
    assert "distance_m" in res
    assert res["distance_m"] > 0

    # Unknown tool
    res_err, err_msg = await execute_canonical_tool("nonexistent_tool", {})
    assert err_msg is not None
    assert "Unknown tool" in err_msg


@pytest.mark.asyncio
async def test_agentic_tool_loop_scripted_success():
    """
    Test autonomous multi-turn loop with a scripted fake provider:
    Turn 1: Model requests query_dependency_graph
    Turn 2: Model requests compute_distance
    Turn 3: Model returns final JSON
    """
    async def scripted_caller(messages, tools, iteration):
        if iteration == 1:
            return {
                "text": "Investigating dependencies first.",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "name": "query_dependency_graph",
                        "arguments": {"issue_type": "WATER_PIPE_BURST"}
                    }
                ]
            }
        elif iteration == 2:
            return {
                "text": "Checking distance to adjacent complaint.",
                "tool_calls": [
                    {
                        "id": "call_2",
                        "name": "compute_distance",
                        "arguments": {"lat1": 19.1136, "lon1": 72.8697, "lat2": 19.1140, "lon2": 72.8700}
                    }
                ]
            }
        else:
            final_json = {
                "root_cause": {
                    "hypothesis": "Burst pipe under arterial road causing localized subsidence.",
                    "chain": ["WATER_PIPE_BURST", "ROAD_CAVE_IN"],
                    "confidence": 0.88,
                    "disclaimer": "AI-generated civic incident hypothesis. Physical inspection recommended."
                },
                "impact_score": {
                    "score": 78,
                    "priority": "HIGH",
                    "breakdown": {"severity_score": 24, "infrastructure_proximity": 18}
                },
                "response_plan": {
                    "steps": [
                        {"step_number": 1, "department": "WATER_BOARD", "action": "Isolate main valve"},
                        {"step_number": 2, "department": "ROADS_DEPT", "action": "Resurface cavity"}
                    ]
                }
            }
            return {
                "text": json.dumps(final_json),
                "tool_calls": []
            }

    cluster_summary = {
        "primary_report_id": "REP_001",
        "primary_description": "Water gushing and road buckling",
        "primary_location": {"latitude": 19.1136, "longitude": 72.8697}
    }

    result = await run_agentic_tool_loop(
        provider="openai",
        api_key="fake-test-key",
        model="gpt-4o-mini",
        system_prompt="Test system prompt",
        cluster_summary=cluster_summary,
        custom_caller=scripted_caller,
    )

    assert result is not None
    assert result["reasoning_mode"] == "agentic_multi_turn"
    assert "query_dependency_graph" in result["tools_used"]
    assert "compute_distance" in result["tools_used"]

    trace = result["agent_trace"]
    assert len(trace) >= 6
    types_in_trace = [t["type"] for t in trace]
    assert "model_call" in types_in_trace
    assert "tool_call" in types_in_trace
    assert "tool_result" in types_in_trace
    assert "final" in types_in_trace


@pytest.mark.asyncio
async def test_agentic_tool_loop_exceeds_iterations():
    """Verify loop cleanly stops when exceeding max_iterations without final JSON."""
    async def endless_caller(messages, tools, iteration):
        return {
            "text": f"Calling tool again in iteration {iteration}",
            "tool_calls": [
                {
                    "id": f"call_{iteration}",
                    "name": "compute_distance",
                    "arguments": {"lat1": 19.1, "lon1": 72.8, "lat2": 19.2, "lon2": 72.9}
                }
            ]
        }

    cluster_summary = {"primary_report_id": "REP_002"}

    result = await run_agentic_tool_loop(
        provider="openai",
        api_key="fake-key",
        model="gpt-4o-mini",
        system_prompt="Test prompt",
        cluster_summary=cluster_summary,
        max_iterations=3,
        custom_caller=endless_caller,
    )

    # Should gracefully return None when max iterations exceeded without final answer
    assert result is None


@pytest.mark.asyncio
async def test_agentic_tool_loop_tool_raising():
    """Verify loop handles a tool raising an exception without crashing."""
    async def raising_tool_caller(messages, tools, iteration):
        if iteration == 1:
            return {
                "text": "Calling broken tool",
                "tool_calls": [
                    {
                        "id": "bad_call",
                        "name": "compute_distance",
                        # Missing required parameters will cause compute_distance to raise KeyError
                        "arguments": {}
                    }
                ]
            }
        else:
            return {
                "text": json.dumps({"root_cause": {"hypothesis": "Recovered despite tool error"}}),
                "tool_calls": []
            }

    cluster_summary = {"primary_report_id": "REP_003"}

    result = await run_agentic_tool_loop(
        provider="openai",
        api_key="fake-key",
        model="gpt-4o-mini",
        system_prompt="Test prompt",
        cluster_summary=cluster_summary,
        custom_caller=raising_tool_caller,
    )

    assert result is not None
    assert result["reasoning_mode"] == "agentic_multi_turn"
    trace = result["agent_trace"]
    tool_result_step = next(t for t in trace if t["type"] == "tool_result")
    assert tool_result_step["error"] is not None
