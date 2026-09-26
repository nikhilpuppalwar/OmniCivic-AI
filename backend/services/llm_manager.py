"""
OmniCivic AI -- Multi-Provider LLM Manager (Security Hardened)
Handles encrypted multi-provider settings management, Fernet encryption at rest,
live ping diagnostics, dynamic model discovery, operator authorization, and audit trail logging.
"""

import json
import os
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional
import httpx
from cryptography.fernet import Fernet
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)
load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"), override=True)

LEGACY_SETTINGS_FILE = os.path.join(DATA_DIR, "llm_settings.json")
ENCRYPTED_CONFIG_FILE = os.path.join(DATA_DIR, "provider_configs.enc.json")
AUDIT_LOG_FILE = os.path.join(DATA_DIR, "agent_logs.json")

# Global async lock for file read/write concurrency
_CONFIG_LOCK = asyncio.Lock()

# ─────────────────────────────────────────────────────────────────────────────
# Security & Fernet Encryption at Rest
# ─────────────────────────────────────────────────────────────────────────────

def get_fernet_key() -> bytes:
    """
    Resolve or generate the symmetric 256-bit Fernet encryption key.
    Order of precedence:
    1. LLM_ENCRYPTION_KEY environment variable.
    2. Local file backend/.secret.key (excluded from git via .gitignore).
    """
    env_key = os.getenv("LLM_ENCRYPTION_KEY")
    if env_key:
        return env_key.strip().encode("utf-8")

    key_file = os.path.join(BASE_DIR, ".secret.key")
    if os.path.exists(key_file):
        try:
            with open(key_file, "rb") as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception as e:
            logger.error(f"[LLM_SECURITY] Error reading .secret.key: {e}")

    # Generate new key outside data/ dir
    new_key = Fernet.generate_key()
    try:
        with open(key_file, "wb") as f:
            f.write(new_key)
        logger.info(f"[LLM_SECURITY] Generated new Fernet encryption key at {key_file}")
    except Exception as e:
        logger.error(f"[LLM_SECURITY] Failed to write .secret.key: {e}")
    return new_key


_FERNET = Fernet(get_fernet_key())


def encrypt_string(plain_text: str) -> str:
    """Encrypt plaintext string using Fernet symmetric encryption."""
    if not plain_text:
        return ""
    return _FERNET.encrypt(plain_text.encode("utf-8")).decode("utf-8")


def decrypt_string(cipher_text: str) -> str:
    """Decrypt Fernet ciphertext string to plaintext."""
    if not cipher_text:
        return ""
    try:
        return _FERNET.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
    except Exception as e:
        logger.warning(f"[LLM_SECURITY] Fernet decryption failed (key change or legacy format): {e}")
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Operator Authorization Token Resolution
# ─────────────────────────────────────────────────────────────────────────────

_PRINTED_OPERATOR_BANNER = False

def print_operator_token_banner(token: str) -> None:
    """Print a high-visibility, copyable operator token banner to console (ASCII-safe for Windows)."""
    global _PRINTED_OPERATOR_BANNER
    if not _PRINTED_OPERATOR_BANNER:
        border = "=" * 72
        banner = (
            f"\n{border}\n"
            f"[!] [SECURITY] OPERATOR ACCESS TOKEN:\n"
            f"    {token}\n\n"
            f"Copy this token to the Settings page token bar, or set it in .env:\n"
            f"    OPERATOR_SECRET_TOKEN={token}\n"
            f"{border}\n"
        )
        try:
            print(banner, flush=True)
        except Exception:
            pass
        _PRINTED_OPERATOR_BANNER = True


def get_operator_token() -> str:
    """
    Resolve the operator secret token required for /api/settings endpoints.
    Order of precedence:
    1. OPERATOR_SECRET_TOKEN environment variable.
    2. Local auto-generated token file backend/.operator_token (.gitignore'd).
    Prints a prominent console banner on every restart until .env is set.
    """
    load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)
    load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"), override=True)
    env_token = os.getenv("OPERATOR_SECRET_TOKEN")
    if env_token and env_token.strip():
        return env_token.strip()

    token_file = os.path.join(BASE_DIR, ".operator_token")
    if os.path.exists(token_file):
        try:
            with open(token_file, "r", encoding="utf-8") as f:
                tok = f.read().strip()
                if tok:
                    print_operator_token_banner(tok)
                    return tok
        except Exception:
            pass

    import secrets
    gen_token = secrets.token_hex(16)
    try:
        with open(token_file, "w", encoding="utf-8") as f:
            f.write(gen_token)
        logger.info(f"[LLM_SECURITY] Auto-generated operator secret token in backend/.operator_token: {gen_token}")
    except Exception as e:
        logger.error(f"[LLM_SECURITY] Failed to write .operator_token: {e}")
    
    print_operator_token_banner(gen_token)
    return gen_token


def validate_operator_token(provided_token: Optional[str]) -> bool:
    """Validate X-Operator-Token header against server operator token."""
    expected = get_operator_token()
    if not provided_token or not provided_token.strip():
        return False
    return provided_token.strip() == expected


# ─────────────────────────────────────────────────────────────────────────────
# Static Provider Capabilities & Catalogs
# ─────────────────────────────────────────────────────────────────────────────

PROVIDER_CAPABILITIES: Dict[str, Dict[str, Any]] = {
    "groq": {
        "name": "Groq Cloud",
        "tag": "Ultra Fast LPU",
        "description": "High-throughput inference with Llama 3.3 and DeepSeek R1 models.",
        "tool_support": "TOOL_CALLING_SUPPORTED",
        "tool_badge": "✓ Tool Calling",
        "default_model": "llama-3.3-70b-versatile",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "deepseek-r1-distill-llama-70b"],
        "allows_custom_model": False
    },
    "openai": {
        "name": "OpenAI (ChatGPT)",
        "tag": "Industry Benchmark",
        "description": "GPT-4o multimodal models supporting structured outputs & function calling.",
        "tool_support": "TOOL_CALLING_SUPPORTED",
        "tool_badge": "✓ Tool Calling",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o", "o3-mini", "o1"],
        "allows_custom_model": False
    },
    "claude": {
        "name": "Anthropic Claude",
        "tag": "Advanced Reasoning",
        "description": "Multi-turn tool-calling agentic loop with Claude Sonnet & Opus.",
        "tool_support": "TOOL_CALLING_SUPPORTED",
        "tool_badge": "✓ Tool Calling",
        "default_model": "claude-3-5-sonnet-20241022",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
        "allows_custom_model": False
    },
    "gemini": {
        "name": "Google Gemini",
        "tag": "Multimodal Flash",
        "description": "Low-latency Gemini Flash and Pro models with pre-flight discovery.",
        "tool_support": "TOOL_CALLING_SUPPORTED",
        "tool_badge": "✓ Tool Calling",
        "default_model": "gemini-flash-latest",
        "models": ["gemini-flash-latest", "gemini-pro-latest", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-lite-latest"],
        "allows_custom_model": False
    },
    "huggingface": {
        "name": "Hugging Face",
        "tag": "Open Weights Router",
        "description": "Inference API routing to open-weights models.",
        "tool_support": "LIMITED_TOOL_SUPPORT",
        "tool_badge": "⚠️ Limited Tool Support",
        "default_model": "meta-llama/Llama-3.3-70B-Instruct",
        "models": [],
        "allows_custom_model": True
    },
    "openrouter": {
        "name": "OpenRouter",
        "tag": "Multi-Model Router",
        "description": "Unified API access across hundreds of hosted LLM models.",
        "tool_support": "LIMITED_TOOL_SUPPORT",
        "tool_badge": "⚠️ Limited Tool Support",
        "default_model": "anthropic/claude-3.5-sonnet",
        "models": [],
        "allows_custom_model": True
    },
    "ollama": {
        "name": "Ollama / Local Custom",
        "tag": "Self-Hosted Local",
        "description": "Local offline inference running via Ollama or custom OpenAI-compatible host.",
        "tool_support": "LIMITED_TOOL_SUPPORT",
        "tool_badge": "⚠️ Limited Tool Support",
        "default_model": "llama3.2",
        "models": [],
        "allows_custom_model": True
    },
    "mock": {
        "name": "Deterministic Simulation",
        "tag": "Zero Key / Fallback",
        "description": "Offline deterministic reasoning engines with keyless tool enrichment.",
        "tool_support": "NO_TOOL_SUPPORT",
        "tool_badge": "🛡️ Deterministic",
        "default_model": "simulation-mode",
        "models": ["simulation-mode"],
        "allows_custom_model": False
    }
}

DEFAULT_MODELS = {k: v["default_model"] for k, v in PROVIDER_CAPABILITIES.items()}

ENV_KEY_MAP: Dict[str, List[str]] = {
    "groq": ["GROQ_API_KEY"],
    "openai": ["OPENAI_API_KEY"],
    "claude": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"],
    "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    "huggingface": ["HF_TOKEN", "HUGGINGFACE_API_KEY", "HF_API_KEY"],
    "hf": ["HF_TOKEN", "HUGGINGFACE_API_KEY", "HF_API_KEY"],
    "openrouter": ["OPENROUTER_API_KEY"]
}


def is_masked_key(key: Optional[str]) -> bool:
    """Check if key string is a masked UI placeholder (e.g. gsk_...3a8b or ••••••••)."""
    if not key:
        return False
    return "••••" in key or "..." in key or key.startswith("sk-••••")


def mask_api_key(key: str) -> str:
    """Mask sensitive API keys for UI display (never return plaintext keys)."""
    if not key or len(key) < 8:
        return "••••••••" if key else ""
    return f"{key[:4]}...{key[-4:]}"


# ─────────────────────────────────────────────────────────────────────────────
# Audit Log Helper
# ─────────────────────────────────────────────────────────────────────────────

def append_config_audit_log(
    event_type: str,
    provider: str,
    operator_action: str,
    details: Dict[str, Any]
) -> None:
    """Log configuration audit events with log_type: config_audit to agent_logs.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+05:30", time.localtime()),
        "log_type": "config_audit",
        "agent": "SYSTEM_CONFIG_AUDIT",
        "event_type": event_type,
        "provider": provider,
        "operator_action": operator_action,
        "details": details
    }

    raw_data = None
    if os.path.exists(AUDIT_LOG_FILE):
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except Exception:
            raw_data = None

    if isinstance(raw_data, dict):
        if "logs" not in raw_data or not isinstance(raw_data["logs"], list):
            raw_data["logs"] = []
        raw_data["logs"].append(entry)
        raw_data["total"] = len(raw_data["logs"])
        to_save = raw_data
    elif isinstance(raw_data, list):
        raw_data.append(entry)
        to_save = raw_data
    else:
        to_save = {"logs": [entry], "total": 1}

    try:
        with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2)
    except Exception as e:
        logger.error(f"[AUDIT] Failed to append config audit log: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Multi-Provider Encrypted Persistence (provider_configs.enc.json)
# ─────────────────────────────────────────────────────────────────────────────

def _load_encrypted_configs_sync() -> Dict[str, Any]:
    """Internal sync loader for encrypted provider configuration store."""
    os.makedirs(DATA_DIR, exist_ok=True)

    # Initialize default structure
    default_data = {
        "active_provider": "mock",
        "providers": {
            "mock": {
                "provider_id": "mock",
                "model": "simulation-mode",
                "encrypted_api_key": "",
                "base_url": "",
                "temperature": 0.0,
                "cached_models": ["simulation-mode"],
                "last_tested": "",
                "last_test_status": "success"
            }
        }
    }

    if not os.path.exists(ENCRYPTED_CONFIG_FILE):
        # Migrate from legacy llm_settings.json if present
        if os.path.exists(LEGACY_SETTINGS_FILE):
            try:
                with open(LEGACY_SETTINGS_FILE, "r", encoding="utf-8") as f:
                    legacy = json.load(f)
                    active_p = legacy.get("provider", "mock")
                    default_data["active_provider"] = active_p
                    p_keys = legacy.get("provider_keys", {})
                    for p_id, p_key in p_keys.items():
                        if p_key and not is_masked_key(p_key):
                            default_data["providers"][p_id] = {
                                "provider_id": p_id,
                                "model": DEFAULT_MODELS.get(p_id, ""),
                                "encrypted_api_key": encrypt_string(p_key),
                                "base_url": legacy.get("base_url", ""),
                                "temperature": float(legacy.get("temperature", 0.3)),
                                "cached_models": [],
                                "last_tested": "",
                                "last_test_status": ""
                            }
            except Exception as e:
                logger.warning(f"[LLM_STORAGE] Error reading legacy settings: {e}")

        # Save initial encrypted store
        try:
            with open(ENCRYPTED_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=2)
        except Exception as e:
            logger.error(f"[LLM_STORAGE] Error writing encrypted config store: {e}")
        return default_data

    try:
        with open(ENCRYPTED_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "active_provider" not in data:
                data["active_provider"] = "mock"
            if "providers" not in data:
                data["providers"] = {}
            if "mock" not in data["providers"]:
                data["providers"]["mock"] = {
                    "provider_id": "mock",
                    "model": "simulation-mode",
                    "encrypted_api_key": "",
                    "base_url": "",
                    "temperature": 0.0,
                    "cached_models": ["simulation-mode"],
                    "last_tested": "",
                    "last_test_status": "success"
                }
            return data
    except Exception as e:
        logger.error(f"[LLM_STORAGE] Failed to load encrypted provider configs: {e}")
        return default_data


def load_encrypted_provider_configs() -> Dict[str, Any]:
    """Public wrapper to read current encrypted provider configurations."""
    return _load_encrypted_configs_sync()


def save_encrypted_provider_configs(data: Dict[str, Any]) -> None:
    """Public wrapper to write encrypted provider configurations."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ENCRYPTED_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# Backward compatibility functions for rest of backend
def load_llm_settings() -> Dict[str, Any]:
    """Compatibility loader: returns dict matching legacy settings format."""
    store = _load_encrypted_configs_sync()
    active_id = store.get("active_provider", "mock")
    p_config = store.get("providers", {}).get(active_id, {})
    raw_key = decrypt_string(p_config.get("encrypted_api_key", "")) if active_id != "mock" else ""

    # Build provider_keys map for backward compatibility
    provider_keys = {}
    for pid, pconf in store.get("providers", {}).items():
        dec_k = decrypt_string(pconf.get("encrypted_api_key", ""))
        if dec_k:
            provider_keys[pid] = dec_k

    return {
        "provider": active_id,
        "api_key": raw_key,
        "model": p_config.get("model", DEFAULT_MODELS.get(active_id, "simulation-mode")),
        "base_url": p_config.get("base_url", ""),
        "temperature": p_config.get("temperature", 0.3),
        "max_tokens": 1000,
        "provider_keys": provider_keys
    }


def get_active_api_key(provider: str, explicit_key: str = "") -> str:
    """
    Resolve API key in order:
    1. explicit_key (if provided and not masked)
    2. Encrypted stored key configured via AI Settings page (provider_configs.enc.json)
    (Environment variable fallback disabled: keys must be managed exclusively via Settings)
    """
    prov = provider.lower().strip()
    if explicit_key and not is_masked_key(explicit_key):
        return explicit_key.strip()

    store = _load_encrypted_configs_sync()
    p_config = store.get("providers", {}).get(prov, {})
    cipher_key = p_config.get("encrypted_api_key", "")
    if cipher_key:
        decrypted = decrypt_string(cipher_key)
        if decrypted:
            return decrypted

    return ""


# ─────────────────────────────────────────────────────────────────────────────
# High-Level Settings Management Functions (With Masked Overwrite Protection)
# ─────────────────────────────────────────────────────────────────────────────

async def save_provider_config(
    provider_id: str,
    api_key: str,
    model: str,
    temperature: float = 0.3,
    base_url: str = "",
    set_active: bool = False
) -> Dict[str, Any]:
    """
    Save or update a provider configuration with MASKED-KEY OVERWRITE PROTECTION.
    If api_key is a masked string (e.g. sk-••••1234), existing encrypted key is preserved.
    """
    prov = provider_id.lower().strip()
    async with _CONFIG_LOCK:
        store = _load_encrypted_configs_sync()
        existing = store.get("providers", {}).get(prov, {})

        # Masked Key Protection & Empty-Field Semantics:
        # 1. If masked placeholder submitted, preserve existing encrypted key in vault
        # 2. Else if new non-empty string provided, encrypt and store new key
        # 3. Else (field cleared to empty string ""), explicitly clear stored key
        raw_key = (api_key or "").strip()
        if is_masked_key(api_key):
            encrypted_key = existing.get("encrypted_api_key", "")
        elif raw_key:
            encrypted_key = encrypt_string(raw_key)
        else:
            encrypted_key = ""

        chosen_model = model.strip() or DEFAULT_MODELS.get(prov, "")
        cached = list(existing.get("cached_models", []))
        if chosen_model and chosen_model not in cached and chosen_model != "simulation-mode":
            cached.insert(0, chosen_model)

        updated_p = {
            "provider_id": prov,
            "model": chosen_model,
            "encrypted_api_key": encrypted_key,
            "base_url": base_url.strip(),
            "temperature": float(temperature),
            "cached_models": cached,
            "last_tested": existing.get("last_tested", ""),
            "last_test_status": existing.get("last_test_status", "")
        }

        store["providers"][prov] = updated_p
        if set_active:
            store["active_provider"] = prov

        save_encrypted_provider_configs(store)

    append_config_audit_log(
        event_type="PROVIDER_SAVED",
        provider=prov,
        operator_action=f"Saved configuration for provider '{prov}' (Model: {updated_p['model']}, Set Active: {set_active})",
        details={"model": updated_p["model"], "temperature": temperature, "set_active": set_active}
    )

    return get_public_settings_payload()


async def set_active_provider(provider_id: str) -> Dict[str, Any]:
    """Switch active provider ID without modifying saved credentials."""
    prov = provider_id.lower().strip()
    async with _CONFIG_LOCK:
        store = _load_encrypted_configs_sync()
        prev_active = store.get("active_provider", "mock")
        if prov not in store.get("providers", {}) and prov != "mock":
            # Auto initialize card entry if selecting new provider
            store["providers"][prov] = {
                "provider_id": prov,
                "model": DEFAULT_MODELS.get(prov, ""),
                "encrypted_api_key": "",
                "base_url": "",
                "temperature": 0.3,
                "cached_models": [],
                "last_tested": "",
                "last_test_status": ""
            }

        store["active_provider"] = prov
        save_encrypted_provider_configs(store)

    append_config_audit_log(
        event_type="ACTIVE_PROVIDER_CHANGED",
        provider=prov,
        operator_action=f"Switched active LLM provider from '{prev_active}' to '{prov}'",
        details={"previous_provider": prev_active, "new_provider": prov}
    )

    return get_public_settings_payload()


async def delete_provider_config(provider_id: str) -> Dict[str, Any]:
    """
    Remove saved credentials for a provider.
    RULES:
    1. Rejects deletion of 'mock' (Deterministic Simulation) with ValueError (HTTP 400).
    2. If deleting the currently active provider, auto-resets active_provider to 'mock'.
    """
    prov = provider_id.lower().strip()
    if prov == "mock":
        raise ValueError("Deterministic Simulation ('mock') is mandatory and cannot be deleted.")

    async with _CONFIG_LOCK:
        store = _load_encrypted_configs_sync()
        active_prov = store.get("active_provider", "mock")

        if prov in store.get("providers", {}):
            del store["providers"][prov]

        was_active = (active_prov == prov)
        if was_active:
            store["active_provider"] = "mock"

        save_encrypted_provider_configs(store)

    append_config_audit_log(
        event_type="PROVIDER_DELETED",
        provider=prov,
        operator_action=f"Deleted credentials for provider '{prov}'. Auto-fallback triggered: {was_active}",
        details={"deleted_provider": prov, "auto_reset_to_mock": was_active}
    )

    return get_public_settings_payload()


def get_public_settings_payload() -> Dict[str, Any]:
    """
    Build public payload for frontend UI:
    Returns provider cards with capability badges, masked keys, and active provider ID.
    Plaintext keys are NEVER exposed.
    """
    store = _load_encrypted_configs_sync()
    active_id = store.get("active_provider", "mock")
    saved_providers = store.get("providers", {})

    providers_payload = []
    for p_id, cap in PROVIDER_CAPABILITIES.items():
        p_saved = saved_providers.get(p_id, {})
        raw_key = decrypt_string(p_saved.get("encrypted_api_key", "")) if p_saved.get("encrypted_api_key") else ""

        masked_key = mask_api_key(raw_key) if raw_key else ""
        has_saved_key = bool(raw_key)

        # Merge static models with dynamically discovered models and custom saved models
        combined_models = list(cap["models"])
        cached_models = p_saved.get("cached_models", [])
        for cm in cached_models:
            if cm and cm not in combined_models:
                combined_models.append(cm)
        curr_m = p_saved.get("model", "")
        if curr_m and curr_m not in combined_models:
            combined_models.append(curr_m)

        providers_payload.append({
            "provider_id": p_id,
            "name": cap["name"],
            "tag": cap["tag"],
            "description": cap["description"],
            "tool_support": cap["tool_support"],
            "tool_badge": cap["tool_badge"],
            "default_model": cap["default_model"],
            "models": combined_models,
            "allows_custom_model": cap["allows_custom_model"],
            "is_active": (p_id == active_id),
            "has_saved_key": has_saved_key,
            "masked_key": masked_key,
            "selected_model": p_saved.get("model", cap["default_model"]),
            "temperature": p_saved.get("temperature", 0.3),
            "base_url": p_saved.get("base_url", ""),
            "last_tested": p_saved.get("last_tested", ""),
            "last_test_status": p_saved.get("last_test_status", "")
        })

    active_config = saved_providers.get(active_id, {})
    return {
        "active_provider": active_id,
        "active_model": active_config.get("model", DEFAULT_MODELS.get(active_id, "simulation-mode")),
        "providers": providers_payload
    }


# ─────────────────────────────────────────────────────────────────────────────
# Per-Provider Exception Normalization Layer
# ─────────────────────────────────────────────────────────────────────────────

def parse_provider_error(provider: str, exc: Exception) -> Dict[str, str]:
    """Map provider-specific SDK / HTTP exceptions into normalized error categories."""
    err_str = str(exc)
    if isinstance(exc, httpx.TimeoutException):
        return {
            "category": "timeout",
            "message": f"Connection Timeout: Server timed out after 10s while reaching {provider} endpoint."
        }

    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        detail_msg = ""
        try:
            err_json = exc.response.json()
            if isinstance(err_json, dict):
                detail = err_json.get("error") or err_json.get("message") or err_json.get("detail")
                if isinstance(detail, dict):
                    detail = detail.get("message") or str(detail)
                detail_msg = str(detail) if detail else exc.response.text[:120]
        except Exception:
            detail_msg = exc.response.text[:120]

        if status_code in (401, 403):
            return {
                "category": "auth_failure",
                "message": f"Authentication Error (HTTP {status_code}): Invalid API key or rejected credentials for {provider}. ({detail_msg})"
            }
        elif status_code == 429:
            return {
                "category": "rate_limit",
                "message": f"Rate Limit Exceeded (HTTP 429): Quota exhausted or rate limited by {provider}. ({detail_msg})"
            }
        elif status_code == 404:
            return {
                "category": "model_not_found",
                "message": f"Model Not Found (HTTP 404): The model string is invalid or unavailable for {provider}. ({detail_msg})"
            }
        else:
            return {
                "category": "network_error",
                "message": f"HTTP {status_code} Error from {provider}: {detail_msg}"
            }

    return {
        "category": "network_error",
        "message": f"Diagnostic error connecting to {provider}: {err_str[:160]}"
    }


# ─────────────────────────────────────────────────────────────────────────────
# Diagnostic Connectivity Ping & Dynamic Model Discovery
# ─────────────────────────────────────────────────────────────────────────────

async def test_llm_connection(
    provider: str,
    api_key: str = "",
    model: str = "",
    base_url: str = ""
) -> Dict[str, Any]:
    """
    Test live LLM connectivity using a lightweight diagnostic ping prompt ("Reply with OK.")
    Enforces a strict 10.0s timeout and performs live ListModels discovery on success.
    """
    prov = provider.lower().strip()
    if prov == "mock":
        return {
            "status": "success",
            "message": "Deterministic Simulation mode active. No remote API key required.",
            "latency_ms": 12,
            "provider": "mock",
            "model": "simulation-mode"
        }

    resolved_key = get_active_api_key(prov, api_key)
    if not resolved_key and prov not in ["ollama", "custom"]:
        return {
            "status": "error",
            "message": f"Authentication Error: No valid API key provided for provider '{prov}'.",
            "category": "auth_failure",
            "latency_ms": 0,
            "provider": prov,
            "model": model
        }

    target_model = model.strip() or DEFAULT_MODELS.get(prov, "gpt-4o-mini")
    start_time = time.time()
    discovered_models: List[str] = []

    # 1. Pre-flight model discovery for Gemini
    if prov == "gemini":
        async with httpx.AsyncClient(timeout=10.0) as probe_client:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={resolved_key}"
            try:
                probe_resp = await probe_client.get(list_url)
                if probe_resp.status_code == 200:
                    probe_data = probe_resp.json()
                    discovered_models = [
                        m["name"].replace("models/", "")
                        for m in probe_data.get("models", [])
                        if "generateContent" in m.get("supportedGenerationMethods", [])
                    ]
                elif probe_resp.status_code in (401, 403):
                    return {
                        "status": "error",
                        "category": "auth_failure",
                        "message": f"Gemini API rejected key (HTTP {probe_resp.status_code}). Generate key at aistudio.google.com",
                        "latency_ms": 0,
                        "provider": prov,
                        "model": target_model
                    }
            except Exception as ex:
                err_norm = parse_provider_error(prov, ex)
                return {
                    "status": "error",
                    "category": err_norm["category"],
                    "message": err_norm["message"],
                    "latency_ms": 0,
                    "provider": prov,
                    "model": target_model
                }

    # 2. Diagnostic ping completion prompt ("Reply with OK.", max_tokens=5, timeout=10.0)
    system_prompt = "You are a network diagnostic probe."
    user_prompt = "Reply with OK."

    try:
        res_text = await generate_completion(
            provider=prov,
            api_key=resolved_key,
            model=target_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            base_url=base_url,
            max_tokens=5,
            temperature=0.0
        )
        latency_ms = int((time.time() - start_time) * 1000)

        # Cache discovered models & last test timestamp in provider config store
        async with _CONFIG_LOCK:
            store = _load_encrypted_configs_sync()
            if prov in store.get("providers", {}):
                store["providers"][prov]["last_tested"] = time.strftime("%Y-%m-%dT%H:%M:%S+05:30", time.localtime())
                store["providers"][prov]["last_test_status"] = "success"
                if discovered_models:
                    store["providers"][prov]["cached_models"] = discovered_models
                save_encrypted_provider_configs(store)

        append_config_audit_log(
            event_type="PROVIDER_PING_TEST",
            provider=prov,
            operator_action=f"Executed diagnostic API ping test for provider '{prov}' (Result: PASS, Latency: {latency_ms}ms)",
            details={"latency_ms": latency_ms, "model": target_model, "status": "success"}
        )

        return {
            "status": "success",
            "message": f"API ping successful ({latency_ms} ms)! Response: '{res_text[:30].strip()}'",
            "latency_ms": latency_ms,
            "provider": prov,
            "model": target_model,
            "discovered_models": discovered_models
        }

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        err_norm = parse_provider_error(prov, e)

        async with _CONFIG_LOCK:
            store = _load_encrypted_configs_sync()
            if prov in store.get("providers", {}):
                store["providers"][prov]["last_tested"] = time.strftime("%Y-%m-%dT%H:%M:%S+05:30", time.localtime())
                store["providers"][prov]["last_test_status"] = err_norm["category"]
                save_encrypted_provider_configs(store)

        append_config_audit_log(
            event_type="PROVIDER_PING_TEST",
            provider=prov,
            operator_action=f"Executed diagnostic API ping test for provider '{prov}' (Result: FAIL - {err_norm['category']})",
            details={"latency_ms": latency_ms, "model": target_model, "status": "error", "error": err_norm["message"]}
        )

        return {
            "status": "error",
            "category": err_norm["category"],
            "message": err_norm["message"],
            "latency_ms": latency_ms,
            "provider": prov,
            "model": target_model
        }


# ─────────────────────────────────────────────────────────────────────────────
# Core LLM Completion Router
# ─────────────────────────────────────────────────────────────────────────────

async def generate_completion(
    provider: str = "",
    api_key: str = "",
    model: str = "",
    system_prompt: str = "You are OmniCivic AI assistant.",
    user_prompt: str = "",
    base_url: str = "",
    max_tokens: int = 800,
    temperature: float = 0.3
) -> str:
    """
    Generate completion using specified or saved LLM configuration.
    Supports OpenAI, Anthropic, Gemini, Groq, Hugging Face, OpenRouter, Ollama, and Mock.
    Enforces a strict 10.0s client timeout.
    """
    settings = load_llm_settings()
    active_provider = (provider or settings.get("provider", "mock")).lower().strip()
    active_key = get_active_api_key(active_provider, api_key)
    active_model = model or settings.get("model", "") or DEFAULT_MODELS.get(active_provider, "gpt-4o-mini")
    active_url = base_url or settings.get("base_url", "")

    if active_provider == "mock" or (not active_key and active_provider not in ["ollama", "custom"]):
        return ""

    async with httpx.AsyncClient(timeout=10.0) as client:

        # 1. Groq (OpenAI Compatible)
        if active_provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {active_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": active_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        # 2. OpenAI / ChatGPT
        elif active_provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {active_key}",
                "Content-Type": "application/json"
            }
            body = {
                "model": active_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        # 3. OpenRouter
        elif active_provider == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {active_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://omnicivic.ai",
                "X-Title": "OmniCivic AI"
            }
            body = {
                "model": active_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        # 4. Anthropic Claude
        elif active_provider in ["claude", "anthropic"]:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": active_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            body = {
                "model": active_model,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]

        # 5. Google Gemini
        elif active_provider == "gemini":
            raw_model = active_model.strip() if active_model else "gemini-2.0-flash"
            clean_model = raw_model.replace("models/", "")

            headers = {"Content-Type": "application/json"}
            body = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"System Instructions: {system_prompt}\n\nUser Request: {user_prompt}"}
                        ]
                    }
                ]
            }

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={active_key}"
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        # 6. Hugging Face Inference API / Router
        elif active_provider in ["huggingface", "hf"]:
            target_model = active_model.strip() or "meta-llama/Llama-3.3-70B-Instruct"
            target_url = active_url if active_url else f"https://api-inference.huggingface.co/models/{target_model}"

            headers = {
                "Authorization": f"Bearer {active_key}",
                "Content-Type": "application/json"
            }

            if "chat/completions" in target_url:
                body = {
                    "model": target_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            else:
                body = {
                    "inputs": f"System: {system_prompt}\nUser: {user_prompt}",
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": max(0.01, temperature)
                    }
                }

            resp = await client.post(target_url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()

            if isinstance(data, dict):
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                elif "generated_text" in data:
                    return data["generated_text"]
                elif "error" in data:
                    raise ValueError(str(data["error"]))
            elif isinstance(data, list) and len(data) > 0:
                item = data[0]
                if isinstance(item, dict) and "generated_text" in item:
                    return item["generated_text"]
                return str(item)
            return str(data)

        # 7. Local Ollama or Custom Base URL
        elif active_provider in ["ollama", "custom"]:
            target_url = active_url.rstrip("/") if active_url else "http://localhost:11434/v1"
            if not target_url.endswith("/chat/completions"):
                target_url = f"{target_url}/chat/completions"

            headers = {"Content-Type": "application/json"}
            if active_key:
                headers["Authorization"] = f"Bearer {active_key}"

            body = {
                "model": active_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature
            }
            resp = await client.post(target_url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        else:
            raise ValueError(f"Unsupported provider: {active_provider}")
