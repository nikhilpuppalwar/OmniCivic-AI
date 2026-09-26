"""
Automated Verification Script for Settings -> AI Model & LLM Provider Configuration.
Verifies operator auth, active_provider invariance, masked key preservation vs empty-field clearing,
deletion rules, config audit logs, and reasoning agent fallback.
"""

import os
import sys
import json
import asyncio
import httpx

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.llm_manager import (
    get_operator_token,
    load_encrypted_provider_configs,
    decrypt_string,
    save_provider_config,
    set_active_provider,
    delete_provider_config,
)
from agents.reasoning_agent import run_agentic_reasoning

API_BASE = "http://localhost:8000"


async def run_all_tests():
    token = get_operator_token()
    print(f"=== Starting Settings Verification (Operator Token: {token[:8]}...) ===")

    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1. Operator Auth Gate
        print("\n[1] Testing Operator Auth Gate...")
        r_no_auth = await client.get(f"{API_BASE}/api/settings")
        assert r_no_auth.status_code == 401, f"Expected 401 without auth, got {r_no_auth.status_code}"
        print("  [OK] Request without token returned 401 Unauthorized")

        r_bad_auth = await client.get(f"{API_BASE}/api/settings", headers={"X-Operator-Token": "invalid_fake_token"})
        assert r_bad_auth.status_code == 401, f"Expected 401 with bad auth, got {r_bad_auth.status_code}"
        print("  [OK] Request with invalid token returned 401 Unauthorized")

        headers = {"X-Operator-Token": token}
        r_auth = await client.get(f"{API_BASE}/api/settings", headers=headers)
        assert r_auth.status_code == 200, f"Expected 200 with valid token, got {r_auth.status_code}"
        data = r_auth.json()
        assert "active_provider" in data
        assert "providers" in data
        assert len(data["providers"]) == 8
        print(f"  [OK] Valid token authenticated successfully. Providers available: {len(data['providers'])}")

        # 2. Test API Connectivity & Invariance of active_provider
        print("\n[2] Testing Diagnostic Ping & Active Provider Invariance...")
        initial_active = data["active_provider"]
        r_test = await client.post(
            f"{API_BASE}/api/settings/test",
            headers=headers,
            json={"provider": "mock"}
        )
        assert r_test.status_code == 200, f"Expected 200, got {r_test.status_code}: {r_test.text}"
        test_data = r_test.json()
        assert test_data["status"] == "success", f"Expected test success, got {test_data}"
        print(f"  [OK] Diagnostic ping against mock passed: {test_data['message']} (Latency: {test_data.get('latency_ms')}ms)")

        # Verify active_provider didn't change
        r_check = await client.get(f"{API_BASE}/api/settings", headers=headers)
        after_active = r_check.json()["active_provider"]
        assert after_active == initial_active, f"Active provider changed unexpectedly! Initial: {initial_active}, After: {after_active}"
        print(f"  [OK] Active provider invariance verified: remaining at '{after_active}'")

        # 3. Masked Key Overwrite Protection & Empty-Field Semantics
        print("\n[3] Testing Masked-Value Overwrite Protection & Empty-Field Clearing...")
        secret_key = "gsk_test_secret_key_8899_xyz"
        r_save1 = await client.post(
            f"{API_BASE}/api/settings",
            headers=headers,
            json={
                "provider_id": "groq",
                "api_key": secret_key,
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.25,
                "set_active": False
            }
        )
        assert r_save1.status_code == 200
        groq_cfg = next(p for p in r_save1.json()["settings"]["providers"] if p["provider_id"] == "groq")
        assert groq_cfg["has_saved_key"] is True
        masked_val = groq_cfg["masked_key"]
        assert "..." in masked_val or "••••" in masked_val
        print(f"  [OK] Saved initial key. Displayed masked placeholder: '{masked_val}'")

        # Verify encryption in storage file
        enc_store = load_encrypted_provider_configs()
        stored_cipher = enc_store["providers"]["groq"]["encrypted_api_key"]
        decrypted = decrypt_string(stored_cipher)
        assert decrypted == secret_key, f"Decryption mismatch! Expected {secret_key}, got {decrypted}"
        print("  [OK] Verified Fernet encryption at rest in provider_configs.enc.json")

        # Now edit parameters while passing the masked placeholder
        r_save2 = await client.post(
            f"{API_BASE}/api/settings",
            headers=headers,
            json={
                "provider_id": "groq",
                "api_key": masked_val,  # masked string submitted!
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.45,
                "set_active": False
            }
        )
        assert r_save2.status_code == 200
        enc_store2 = load_encrypted_provider_configs()
        decrypted2 = decrypt_string(enc_store2["providers"]["groq"]["encrypted_api_key"])
        assert decrypted2 == secret_key, f"Masked overwrite protection FAILED! Expected {secret_key}, got {decrypted2}"
        assert enc_store2["providers"]["groq"]["temperature"] == 0.45
        print("  [OK] Masked-key overwrite protection PASSED: secret key retained in vault while updating temperature to 0.45")

        # Now test empty field clearing: clearing input string should delete the key
        r_save3 = await client.post(
            f"{API_BASE}/api/settings",
            headers=headers,
            json={
                "provider_id": "groq",
                "api_key": "",  # explicitly cleared!
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.3,
                "set_active": False
            }
        )
        assert r_save3.status_code == 200
        enc_store3 = load_encrypted_provider_configs()
        assert enc_store3["providers"]["groq"]["encrypted_api_key"] == "", "Empty string should clear the stored key"
        print("  [OK] Empty-field clearing PASSED: submitting empty string successfully cleared stored key")

        # 4. Multi-Provider Switching & Deletion Rules
        print("\n[4] Testing Multi-Provider Switching & Deletion Rules...")
        # Save a key for groq and set it as active
        await client.post(
            f"{API_BASE}/api/settings",
            headers=headers,
            json={
                "provider_id": "groq",
                "api_key": "gsk_active_groq_key_1122",
                "model": "llama-3.3-70b-versatile",
                "set_active": True
            }
        )
        r_active = await client.get(f"{API_BASE}/api/settings", headers=headers)
        assert r_active.json()["active_provider"] == "groq"
        print("  [OK] Successfully set 'groq' as active provider")

        # Attempt to delete mock -> should be rejected with 400
        r_del_mock = await client.delete(f"{API_BASE}/api/settings/provider/mock", headers=headers)
        assert r_del_mock.status_code == 400, f"Expected 400 when deleting mock, got {r_del_mock.status_code}"
        print(f"  [OK] Deleting 'mock' rejected with HTTP 400: '{r_del_mock.json().get('detail')}'")

        # Delete the active provider ('groq') -> should auto reset active_provider to mock
        r_del_active = await client.delete(f"{API_BASE}/api/settings/provider/groq", headers=headers)
        assert r_del_active.status_code == 200
        del_data = r_del_active.json()
        assert del_data["settings"]["active_provider"] == "mock", f"Expected auto-reset to 'mock', got {del_data['settings']['active_provider']}"
        print("  [OK] Deleting active provider successfully auto-reset active_provider to 'mock'")

        # 5. Check Audit Logs for log_type: config_audit
        print("\n[5] Verifying Audit Trail in agent_logs.json...")
        logs_path = os.path.join(BASE_DIR, "data", "agent_logs.json")
        assert os.path.exists(logs_path), "agent_logs.json should exist"
        with open(logs_path, "r", encoding="utf-8") as f:
            all_logs = json.load(f)
        entries = all_logs.get("logs", []) if isinstance(all_logs, dict) else all_logs
        config_logs = [l for l in entries if isinstance(l, dict) and l.get("log_type") == "config_audit"]
        assert len(config_logs) > 0, "Expected at least one config_audit entry in agent_logs.json"
        print(f"  [OK] Verified {len(config_logs)} audit entries tagged with 'log_type: config_audit'")

        # 6. Reasoning Agent Reliability & Fallback
        print("\n[6] Testing Civic Reasoning Agent Fallback with Deliberately Invalid Key...")
        # Configure active provider to OpenAI with broken key
        await client.post(
            f"{API_BASE}/api/settings",
            headers=headers,
            json={
                "provider_id": "openai",
                "api_key": "sk-deliberately-broken-invalid-key",
                "model": "gpt-4o-mini",
                "set_active": True
            }
        )

        mock_report = {
            "report_id": "CIV-TEST-001",
            "description": "Water pipe leak causing sinkhole near hospital junction",
            "location": {"latitude": 19.1136, "longitude": 72.8697, "address": "Andheri East"},
            "issue_type": "WATER_LEAKAGE"
        }
        fallback_result = await run_agentic_reasoning(
            primary_report=mock_report,
            cluster_reports=[],
            cluster_type="CONNECTED"
        )
        assert fallback_result is not None
        assert fallback_result.get("reasoning_mode") == "deterministic_fallback", \
            f"Expected reasoning_mode: deterministic_fallback, got {fallback_result.get('reasoning_mode')}"
        assert "root_cause" in fallback_result
        assert "impact_score" in fallback_result
        assert "response_plan" in fallback_result
        print(f"  [OK] Reasoning agent fallback PASSED: successfully caught failure and returned deterministic_fallback output")

        # Reset active provider back to mock
        await client.post(f"{API_BASE}/api/settings/set-active", headers=headers, json={"provider_id": "mock"})
        print("  [OK] Restored active provider to 'mock'")

    print("\n" + "=" * 70)
    print("ALL 6 AUTOMATED VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
