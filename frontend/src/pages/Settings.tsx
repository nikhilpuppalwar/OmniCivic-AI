import React, { useState, useEffect } from 'react';
import {
  api,
  type PublicSettingsPayload,
  type ProviderConfig,
  type LLMTestResult,
  getStoredOperatorToken,
  setStoredOperatorToken,
} from '../lib/api';
import {
  Cpu,
  Zap,
  Activity,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Save,
  Eye,
  EyeOff,
  Sliders,
  Sparkles,
  Lock,
  Trash2,
  ShieldCheck,
  Check,
  Shield,
  Clock,
  Terminal,
} from 'lucide-react';

import groqLogo from '../assets/groq.png';
import openaiLogo from '../assets/openai.svg';
import claudeLogo from '../assets/claude-color.svg';
import geminiLogo from '../assets/gemini-color.svg';
import hfLogo from '../assets/huggingface-color.svg';
import openrouterLogo from '../assets/openrouter-color.svg';
import ollamaLogo from '../assets/ollama.svg';

const LOGO_MAP: Record<string, string> = {
  groq: groqLogo,
  openai: openaiLogo,
  claude: claudeLogo,
  gemini: geminiLogo,
  huggingface: hfLogo,
  openrouter: openrouterLogo,
  ollama: ollamaLogo,
};

const STATIC_PROVIDERS_FALLBACK: ProviderConfig[] = [
  {
    provider_id: 'groq',
    name: 'Groq Cloud',
    tag: 'Ultra Fast LPU',
    description: 'High-throughput inference with Llama 3.3 and DeepSeek R1 models.',
    tool_support: 'TOOL_CALLING_SUPPORTED',
    tool_badge: '✓ Tool Calling',
    default_model: 'llama-3.3-70b-versatile',
    models: ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768', 'deepseek-r1-distill-llama-70b'],
    allows_custom_model: false,
    is_active: false,
    has_saved_key: false,
    masked_key: '',
    selected_model: 'llama-3.3-70b-versatile',
    temperature: 0.3,
    base_url: '',
    last_tested: '',
    last_test_status: '',
  },
  {
    provider_id: 'openai',
    name: 'OpenAI (ChatGPT)',
    tag: 'Industry Benchmark',
    description: 'GPT-4o multimodal models supporting structured outputs & function calling.',
    tool_support: 'TOOL_CALLING_SUPPORTED',
    tool_badge: '✓ Tool Calling',
    default_model: 'gpt-4o-mini',
    models: ['gpt-4o-mini', 'gpt-4o', 'o3-mini', 'o1'],
    allows_custom_model: false,
    is_active: false,
    has_saved_key: false,
    masked_key: '',
    selected_model: 'gpt-4o-mini',
    temperature: 0.3,
    base_url: '',
    last_tested: '',
    last_test_status: '',
  },
  {
    provider_id: 'claude',
    name: 'Anthropic Claude',
    tag: 'Advanced Reasoning',
    description: 'Multi-turn tool-calling agentic loop with Claude Sonnet & Opus.',
    tool_support: 'TOOL_CALLING_SUPPORTED',
    tool_badge: '✓ Tool Calling',
    default_model: 'claude-3-5-sonnet-20241022',
    models: ['claude-3-5-sonnet-20241022', 'claude-3-7-sonnet-20250219', 'claude-3-5-haiku-20241022', 'claude-3-opus-20240229'],
    allows_custom_model: false,
    is_active: false,
    has_saved_key: false,
    masked_key: '',
    selected_model: 'claude-3-5-sonnet-20241022',
    temperature: 0.3,
    base_url: '',
    last_tested: '',
    last_test_status: '',
  },
  {
    provider_id: 'gemini',
    name: 'Google Gemini',
    tag: 'Multimodal Flash',
    description: 'Low-latency Gemini 2.0 Flash models with pre-flight discovery.',
    tool_support: 'TOOL_CALLING_SUPPORTED',
    tool_badge: '✓ Tool Calling',
    default_model: 'gemini-2.0-flash',
    models: ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-1.5-pro', 'gemini-2.0-flash-lite'],
    allows_custom_model: false,
    is_active: false,
    has_saved_key: false,
    masked_key: '',
    selected_model: 'gemini-2.0-flash',
    temperature: 0.3,
    base_url: '',
    last_tested: '',
    last_test_status: '',
  },
  {
    provider_id: 'huggingface',
    name: 'Hugging Face',
    tag: 'Open Weights Router',
    description: 'Inference API routing to open-weights models.',
    tool_support: 'LIMITED_TOOL_SUPPORT',
    tool_badge: '⚠️ Limited Tool Support',
    default_model: 'meta-llama/Llama-3.3-70B-Instruct',
    models: [],
    allows_custom_model: true,
    is_active: false,
    has_saved_key: false,
    masked_key: '',
    selected_model: 'meta-llama/Llama-3.3-70B-Instruct',
    temperature: 0.3,
    base_url: '',
    last_tested: '',
    last_test_status: '',
  },
  {
    provider_id: 'openrouter',
    name: 'OpenRouter',
    tag: 'Multi-Model Router',
    description: 'Unified API access across hundreds of hosted LLM models.',
    tool_support: 'LIMITED_TOOL_SUPPORT',
    tool_badge: '⚠️ Limited Tool Support',
    default_model: 'anthropic/claude-3.5-sonnet',
    models: [],
    allows_custom_model: true,
    is_active: false,
    has_saved_key: false,
    masked_key: '',
    selected_model: 'anthropic/claude-3.5-sonnet',
    temperature: 0.3,
    base_url: '',
    last_tested: '',
    last_test_status: '',
  },
  {
    provider_id: 'ollama',
    name: 'Ollama / Local Custom',
    tag: 'Self-Hosted Local',
    description: 'Local offline inference running via Ollama or custom OpenAI-compatible host.',
    tool_support: 'LIMITED_TOOL_SUPPORT',
    tool_badge: '⚠️ Limited Tool Support',
    default_model: 'llama3.2',
    models: [],
    allows_custom_model: true,
    is_active: false,
    has_saved_key: false,
    masked_key: '',
    selected_model: 'llama3.2',
    temperature: 0.3,
    base_url: '',
    last_tested: '',
    last_test_status: '',
  },
  {
    provider_id: 'mock',
    name: 'Deterministic Simulation',
    tag: 'Zero Key / Fallback',
    description: 'Offline deterministic reasoning engines with keyless tool enrichment.',
    tool_support: 'NO_TOOL_SUPPORT',
    tool_badge: '🛡️ Deterministic',
    default_model: 'simulation-mode',
    models: ['simulation-mode'],
    allows_custom_model: false,
    is_active: true,
    has_saved_key: false,
    masked_key: '',
    selected_model: 'simulation-mode',
    temperature: 0.0,
    base_url: '',
    last_tested: '',
    last_test_status: 'success',
  },
];

export const Settings: React.FC = () => {
  // Operator Token Session State
  const [operatorToken, setOperatorTokenState] = useState<string>(getStoredOperatorToken());
  const [showOperatorToken, setShowOperatorToken] = useState<boolean>(false);
  const [isTokenSaved, setIsTokenSaved] = useState<boolean>(!!getStoredOperatorToken());
  const [authError, setAuthError] = useState<string | null>(null);

  // Settings Payload State
  const [settingsPayload, setSettingsPayload] = useState<PublicSettingsPayload | null>(null);
  const [selectedProviderId, setSelectedProviderId] = useState<string>('mock');

  // Form State for Selected Provider
  const [apiKey, setApiKey] = useState<string>('');
  const [showKey, setShowKey] = useState<boolean>(false);
  const [model, setModel] = useState<string>('simulation-mode');
  const [baseUrl, setBaseUrl] = useState<string>('');
  const [temperature, setTemperature] = useState<number>(0.3);
  const [isCustomModelMode, setIsCustomModelMode] = useState<boolean>(false);

  // Async Execution States
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isTesting, setIsTesting] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [isActivating, setIsActivating] = useState<boolean>(false);

  // 3-Second Client-Side Debounce Cooldown
  const [cooldown, setCooldown] = useState<number>(0);

  // Diagnostic Test and Feedback States
  const [testResult, setTestResult] = useState<LLMTestResult | null>(null);
  const [notification, setNotification] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  // Cooldown countdown effect
  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [cooldown]);

  // Initial Load
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setIsLoading(true);
    setAuthError(null);
    try {
      const data = await api.getSettings();
      setSettingsPayload(data);
      const activeId = data.active_provider || 'mock';
      setSelectedProviderId((curr) => {
        const target = curr && curr !== 'mock' ? curr : activeId;
        syncFormWithProvider(data, target);
        return target;
      });
    } catch (err: any) {
      if (err.status === 401 || String(err.message).includes('401')) {
        // Attempt automatic dev operator token discovery from backend server
        try {
          const devRes = await api.getDevOperatorToken();
          if (devRes && devRes.token) {
            setStoredOperatorToken(devRes.token);
            setOperatorTokenState(devRes.token);
            setIsTokenSaved(true);
            const retryData = await api.getSettings();
            setSettingsPayload(retryData);
            const activeId = retryData.active_provider || 'mock';
            setSelectedProviderId(activeId);
            syncFormWithProvider(retryData, activeId);
            setAuthError(null);
            return;
          }
        } catch {
          // Dev-token endpoint unavailable or manual token needed
        }

        setAuthError(
          'Operator Authentication Required (HTTP 401). Note: Enter your server Operator Access Token here, NOT your LLM API Key (like Gemini or OpenAI).'
        );
      } else {
        setNotification({
          type: 'error',
          message: err.message || 'Failed to connect to backend settings service.',
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const syncFormWithProvider = (payload: PublicSettingsPayload, provId: string) => {
    const prov = payload.providers.find((p) => p.provider_id === provId);
    if (prov) {
      setApiKey(prov.masked_key || '');
      const activeM = prov.selected_model || prov.default_model || '';
      setModel(activeM);
      setBaseUrl(prov.base_url || '');
      setTemperature(prov.temperature ?? 0.3);
      if (prov.allows_custom_model) {
        setIsCustomModelMode(true);
      } else {
        const inCatalog = prov.models && prov.models.includes(activeM);
        setIsCustomModelMode(!inCatalog && activeM !== 'simulation-mode');
      }
    }
    setTestResult(null);
  };

  const handleSelectProvider = (provId: string) => {
    setSelectedProviderId(provId);
    if (settingsPayload) {
      syncFormWithProvider(settingsPayload, provId);
    } else {
      const fallback = STATIC_PROVIDERS_FALLBACK.find((p) => p.provider_id === provId);
      if (fallback) {
        setApiKey(fallback.masked_key || '');
        const activeM = fallback.selected_model || fallback.default_model || '';
        setModel(activeM);
        setBaseUrl(fallback.base_url || '');
        setTemperature(fallback.temperature ?? 0.3);
        setIsCustomModelMode(fallback.allows_custom_model);
      }
    }
  };

  const handleSaveOperatorToken = () => {
    const trimmed = operatorToken.trim();
    setStoredOperatorToken(trimmed);
    setIsTokenSaved(!!trimmed);
    setNotification({
      type: 'success',
      message: trimmed ? 'Operator access token saved to browser session.' : 'Operator access token cleared.',
    });
    setAuthError(null);
    loadSettings();
  };

  const handleAutoFillDevToken = async () => {
    try {
      const res = await api.getDevOperatorToken();
      if (res && res.token) {
        setOperatorTokenState(res.token);
        setStoredOperatorToken(res.token);
        setIsTokenSaved(true);
        setAuthError(null);
        setNotification({
          type: 'success',
          message: 'Server operator token retrieved and saved to browser session!',
        });
        await loadSettings();
      }
    } catch (err: any) {
      setNotification({
        type: 'error',
        message: 'Could not automatically retrieve server operator token: ' + err.message,
      });
    }
  };

  const providersToRender = settingsPayload?.providers && settingsPayload.providers.length > 0
    ? settingsPayload.providers
    : STATIC_PROVIDERS_FALLBACK;

  const selectedProvider = providersToRender.find((p) => p.provider_id === selectedProviderId) || providersToRender[7];
  const activeProvider = providersToRender.find((p) => p.provider_id === (settingsPayload?.active_provider || 'mock')) || providersToRender[7];

  const handleTestConnection = async () => {
    if (cooldown > 0) return;
    if (selectedProvider?.allows_custom_model && !model.trim()) {
      setNotification({
        type: 'error',
        message: 'Please enter a valid Model Identifier before running the connectivity ping.',
      });
      return;
    }

    setIsTesting(true);
    setTestResult(null);
    setNotification(null);
    try {
      const res = await api.testSettings({
        provider: selectedProviderId,
        api_key: apiKey,
        model: model.trim(),
        base_url: baseUrl.trim(),
      });
      setTestResult(res);

      if (res.discovered_models && res.discovered_models.length > 0 && settingsPayload) {
        const updatedProviders = settingsPayload.providers.map((p) => {
          if (p.provider_id === selectedProviderId) {
            const combined = Array.from(new Set([...p.models, ...(res.discovered_models || [])]));
            return { ...p, models: combined, last_tested: 'Just now', last_test_status: 'success' };
          }
          return p;
        });
        setSettingsPayload({ ...settingsPayload, providers: updatedProviders });
      }
    } catch (err: any) {
      if (err.status === 401 || String(err.message).includes('401')) {
        setAuthError(
          'Operator Authentication Required (HTTP 401). Check backend terminal startup output for your access token.'
        );
      } else {
        setTestResult({
          status: 'error',
          category: 'network_error',
          message: err.message || 'Diagnostic ping failed to reach server.',
          latency_ms: 0,
          provider: selectedProviderId,
          model,
        });
      }
    } finally {
      setIsTesting(false);
      setCooldown(3); // 3-second client-side debounce cooldown
    }
  };

  // Provider-specific API key format hints
  // Each provider can have MULTIPLE valid prefixes (Google/OpenAI have changed formats over time)
  const KEY_FORMAT_HINTS: Record<string, { prefixes: string[]; example: string; guide: string }> = {
    openai: {
      prefixes: ['sk-'],            // covers sk-proj-..., sk-..., sk-test-... all start with sk-
      example: 'sk-proj-... or sk-...',
      guide: 'Get yours at platform.openai.com/api-keys',
    },
    groq: {
      prefixes: ['gsk_'],
      example: 'gsk_...',
      guide: 'Get yours at console.groq.com/keys',
    },
    claude: {
      prefixes: ['sk-ant-'],        // covers sk-ant-api03-... and sk-ant-api-...
      example: 'sk-ant-api03-...',
      guide: 'Get yours at console.anthropic.com/account/keys',
    },
    gemini: {
      prefixes: ['AIzaSy', 'AQ.'],  // AIzaSy = legacy, AQ. = newer Google AI Studio format
      example: 'AIzaSy... or AQ.Ab8...',
      guide: 'Get yours at aistudio.google.com/apikey',
    },
    huggingface: {
      prefixes: ['hf_'],
      example: 'hf_...',
      guide: 'Get yours at huggingface.co/settings/tokens',
    },
    openrouter: {
      prefixes: ['sk-or-'],
      example: 'sk-or-v1-...',
      guide: 'Get yours at openrouter.ai/keys',
    },
  };

  const getKeyFormatWarning = (provId: string, key: string): string | null => {
    if (!key || key.includes('\u2022') || key.includes('...')) return null; // masked placeholder
    const hint = KEY_FORMAT_HINTS[provId];
    if (!hint) return null;
    const isValid = hint.prefixes.some((prefix) => key.startsWith(prefix));
    if (!isValid) {
      const provName = provId.charAt(0).toUpperCase() + provId.slice(1);
      return `This doesn't look like a valid ${provName} key. Expected format: ${hint.example}`;
    }
    return null;
  };


  const handleSaveConfig = async (e: React.FormEvent, activateNow: boolean = false) => {
    e.preventDefault();
    if (selectedProvider?.allows_custom_model && !model.trim()) {
      setNotification({
        type: 'error',
        message: 'Please enter a valid Model Identifier before saving.',
      });
      return;
    }

    // Warn if key format looks wrong (but still allow save — user may know better)
    const keyWarning = getKeyFormatWarning(selectedProviderId, apiKey);
    if (keyWarning) {
      const proceed = window.confirm(
        `Key format warning:\n${keyWarning}\n\nDo you still want to save this key?`
      );
      if (!proceed) return;
    }

    setIsSaving(true);
    setNotification(null);
    try {
      const res = await api.saveProviderSettings({
        provider_id: selectedProviderId,
        api_key: apiKey,
        model: model.trim(),
        base_url: baseUrl.trim(),
        temperature,
        set_active: activateNow,
      });

      setSettingsPayload(res.settings);
      syncFormWithProvider(res.settings, selectedProviderId);
      setNotification({
        type: 'success',
        message: activateNow
          ? `Saved and set ${selectedProvider?.name} as the active reasoning engine!`
          : `Configuration for ${selectedProvider?.name} saved persistently.`,
      });
    } catch (err: any) {
      if (err.status === 401 || String(err.message).includes('401')) {
        setAuthError('Operator Authentication Required (HTTP 401). Click Auto-Fill Server Token to authenticate.');
      } else {
        setNotification({
          type: 'error',
          message: err.message || 'Failed to save configuration.',
        });
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleSetActive = async () => {
    if (selectedProviderId === settingsPayload?.active_provider) return;
    setIsActivating(true);
    setNotification(null);
    try {
      const res = await api.setActiveProvider(selectedProviderId);
      setSettingsPayload(res.settings);
      setNotification({
        type: 'success',
        message: `Active LLM provider switched to ${selectedProvider?.name}!`,
      });
    } catch (err: any) {
      if (err.status === 401 || String(err.message).includes('401')) {
        setAuthError('Operator Authentication Required (HTTP 401). Click Auto-Fill Server Token to authenticate.');
      } else {
        setNotification({
          type: 'error',
          message: err.message || 'Failed to set active provider.',
        });
      }
    } finally {
      setIsActivating(false);
    }
  };

  const handleDeleteKey = async () => {
    if (selectedProviderId === 'mock') return;
    const confirmed = window.confirm(
      `Are you sure you want to remove the saved credentials for ${selectedProvider?.name}?`
    );
    if (!confirmed) return;

    setIsDeleting(true);
    setNotification(null);
    try {
      const res = await api.deleteProvider(selectedProviderId);
      setSettingsPayload(res.settings);
      syncFormWithProvider(res.settings, selectedProviderId);
      setNotification({
        type: 'info',
        message: `Credentials for ${selectedProvider?.name} removed. Active provider: ${res.settings.active_provider}`,
      });
    } catch (err: any) {
      setNotification({
        type: 'error',
        message: err.message || 'Failed to delete provider credentials.',
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const getToolBadgeColor = (badge: string) => {
    if (badge.includes('✓')) {
      return {
        bg: 'rgba(16, 185, 129, 0.12)',
        border: 'rgba(16, 185, 129, 0.3)',
        color: 'var(--status-resolved)',
      };
    }
    if (badge.includes('⚠️')) {
      return {
        bg: 'rgba(245, 158, 11, 0.12)',
        border: 'rgba(245, 158, 11, 0.3)',
        color: 'var(--status-high)',
      };
    }
    return {
      bg: 'rgba(37, 99, 235, 0.12)',
      border: 'rgba(37, 99, 235, 0.3)',
      color: 'var(--accent-blue)',
    };
  };

  if (isLoading && !settingsPayload && !authError) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-secondary)' }}>
          <RefreshCw size={22} className="animate-spin" color="var(--accent-blue)" />
          <span style={{ fontSize: 14, fontWeight: 600 }}>Connecting to OmniCivic AI intelligence vault...</span>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '24px 16px' }} className="animate-fade-in">
      {/* Header Banner */}
      <div
        className="card"
        style={{
          padding: '24px 28px',
          marginBottom: 20,
          background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.12) 0%, rgba(13, 148, 136, 0.08) 100%)',
          borderLeft: '4px solid var(--accent-blue)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 16,
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <Cpu size={22} color="var(--accent-blue)" />
            <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
              AI Model &amp; LLM Provider Configuration
            </h1>
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0, maxWidth: 680, lineHeight: 1.5 }}>
            Configure and switch between AI reasoning providers for root-cause synthesis and multi-department dispatch
            plans. All credentials are encrypted at rest with automatic zero-downtime fallback to Deterministic Simulation.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              padding: '6px 14px',
              borderRadius: 20,
              fontSize: 12,
              fontWeight: 700,
              background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
              color: '#ffffff',
              boxShadow: '0 0 12px rgba(16, 185, 129, 0.35)',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <Sparkles size={14} />
            Active: {activeProvider?.name || 'Deterministic Simulation'}
          </div>
        </div>
      </div>

      {/* Operator Session Access Token Bar */}
      <div
        className="card"
        style={{
          padding: '14px 20px',
          marginBottom: 20,
          background: isTokenSaved ? 'rgba(37, 99, 235, 0.04)' : 'rgba(245, 158, 11, 0.06)',
          border: `1px solid ${isTokenSaved ? 'var(--border-primary)' : 'rgba(245, 158, 11, 0.3)'}`,
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Terminal size={16} color={isTokenSaved ? 'var(--accent-blue)' : 'var(--status-high)'} />
            <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
              Operator Authorization Session
            </span>
            <span
              style={{
                fontSize: 11,
                padding: '2px 8px',
                borderRadius: 10,
                fontWeight: 600,
                background: isTokenSaved ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                color: isTokenSaved ? 'var(--status-resolved)' : 'var(--status-high)',
              }}
            >
              {isTokenSaved ? 'Session Active' : 'Token Not Configured'}
            </span>
          </div>
          <span style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>
            Header: <code>X-Operator-Token</code> &bull; Server Key (Not LLM API Key)
          </span>
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: 260 }}>
            <input
              type={showOperatorToken ? 'text' : 'password'}
              value={operatorToken}
              onChange={(e) => setOperatorTokenState(e.target.value)}
              placeholder="Enter server operator token (or click 'Auto-Fill from Server')..."
              style={{
                width: '100%',
                padding: '8px 36px 8px 12px',
                borderRadius: 6,
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-primary)',
                color: 'var(--text-primary)',
                fontSize: 12,
                fontFamily: 'monospace',
              }}
            />
            <button
              type="button"
              onClick={() => setShowOperatorToken(!showOperatorToken)}
              style={{
                position: 'absolute',
                right: 10,
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: 'var(--text-tertiary)',
                cursor: 'pointer',
              }}
            >
              {showOperatorToken ? <EyeOff size={14} /> : <Eye size={14} />}
            </button>
          </div>

          <button
            type="button"
            onClick={handleSaveOperatorToken}
            style={{
              padding: '8px 16px',
              borderRadius: 6,
              fontSize: 12,
              fontWeight: 700,
              background: 'var(--bg-elevated)',
              color: 'var(--accent-blue)',
              border: '1px solid var(--accent-blue)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              transition: 'all 0.15s ease',
            }}
          >
            <Check size={14} />
            Save Token
          </button>

          <button
            type="button"
            onClick={handleAutoFillDevToken}
            title="Fetch active operator token directly from backend server"
            style={{
              padding: '8px 16px',
              borderRadius: 6,
              fontSize: 12,
              fontWeight: 700,
              background: 'rgba(13, 148, 136, 0.15)',
              color: 'var(--accent-teal)',
              border: '1px solid var(--accent-teal)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              transition: 'all 0.15s ease',
            }}
          >
            <Zap size={14} />
            Auto-Fill from Server
          </button>
        </div>
      </div>

      {/* 401 Auth Error Prompt Banner */}
      {authError && (
        <div
          className="animate-fade-in"
          style={{
            padding: '16px 20px',
            borderRadius: 8,
            marginBottom: 20,
            fontSize: 13,
            fontWeight: 600,
            display: 'flex',
            alignItems: 'flex-start',
            gap: 14,
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid var(--status-critical)',
            color: 'var(--status-critical)',
          }}
        >
          <AlertTriangle size={22} style={{ flexShrink: 0, marginTop: 2 }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 800, fontSize: 14, marginBottom: 4 }}>{authError}</div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontWeight: 400, lineHeight: 1.5, marginBottom: 10 }}>
              The value in the Operator Authorization bar does not match the server's operator access token (for instance, if an LLM API key like <code>AQ.Ab8RN6...</code> was entered instead of the operator secret).
              Click below to automatically retrieve and apply the active operator token from your local server:
            </div>
            <button
              type="button"
              onClick={handleAutoFillDevToken}
              style={{
                padding: '8px 18px',
                borderRadius: 6,
                fontSize: 12,
                fontWeight: 700,
                background: 'var(--accent-blue)',
                color: '#ffffff',
                border: 'none',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                boxShadow: '0 0 12px rgba(37, 99, 235, 0.4)',
              }}
            >
              <Zap size={14} />
              Auto-Fill Server Token &amp; Connect
            </button>
          </div>
        </div>
      )}

      {/* Global Notifications */}
      {notification && (
        <div
          className="animate-fade-in"
          style={{
            padding: '12px 16px',
            borderRadius: 8,
            marginBottom: 20,
            fontSize: 13,
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            background:
              notification.type === 'success'
                ? 'rgba(16, 185, 129, 0.12)'
                : notification.type === 'info'
                ? 'rgba(37, 99, 235, 0.12)'
                : 'rgba(239, 68, 68, 0.12)',
            border: `1px solid ${
              notification.type === 'success'
                ? 'var(--status-resolved)'
                : notification.type === 'info'
                ? 'var(--accent-blue)'
                : 'var(--status-critical)'
            }`,
            color:
              notification.type === 'success'
                ? 'var(--status-resolved)'
                : notification.type === 'info'
                ? 'var(--accent-blue)'
                : 'var(--status-critical)',
          }}
        >
          {notification.type === 'success' ? (
            <CheckCircle2 size={18} />
          ) : notification.type === 'info' ? (
            <Sparkles size={18} />
          ) : (
            <AlertTriangle size={18} />
          )}
          <span>{notification.message}</span>
        </div>
      )}

      {/* 1. Multi-Provider Cards Grid */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <label style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
            1. Select AI Reasoning Provider
          </label>
          <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
            Click card to configure parameters or switch active engine
          </span>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
            gap: 12,
          }}
        >
          {providersToRender.map((p) => {
            const isSelected = selectedProviderId === p.provider_id;
            const isActive = settingsPayload ? p.is_active : p.provider_id === 'mock';
            const badgeStyle = getToolBadgeColor(p.tool_badge);
            const logoSrc = LOGO_MAP[p.provider_id];

            return (
              <div
                key={p.provider_id}
                onClick={() => handleSelectProvider(p.provider_id)}
                style={{
                  padding: '16px',
                  borderRadius: 10,
                  cursor: 'pointer',
                  background: isSelected ? 'rgba(37, 99, 235, 0.08)' : 'var(--bg-secondary)',
                  border: isSelected ? '2px solid var(--accent-blue)' : '1px solid var(--border-primary)',
                  boxShadow: isSelected ? '0 0 16px rgba(37, 99, 235, 0.3)' : 'none',
                  transition: 'all 0.2s ease',
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  {/* Card Header with Logo, Active, and Saved Status */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                    <div
                      style={{
                        width: 34,
                        height: 34,
                        borderRadius: 8,
                        background: 'rgba(255, 255, 255, 0.04)',
                        border: '1px solid var(--border-primary)',
                        padding: 5,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {logoSrc ? (
                        <img src={logoSrc} alt={p.name} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                      ) : (
                        <ShieldCheck size={20} color="var(--accent-blue)" />
                      )}
                    </div>

                    <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                      {isActive && (
                        <span
                          style={{
                            fontSize: 9,
                            fontWeight: 800,
                            padding: '2px 7px',
                            borderRadius: 12,
                            background: 'linear-gradient(135deg, #10B981, #059669)',
                            color: '#ffffff',
                            letterSpacing: '0.04em',
                            boxShadow: '0 0 8px rgba(16, 185, 129, 0.4)',
                          }}
                        >
                          ACTIVE
                        </span>
                      )}
                      {p.has_saved_key && p.provider_id !== 'mock' && (
                        <span
                          title="Credentials encrypted and saved in backend vault"
                          style={{
                            fontSize: 10,
                            fontWeight: 700,
                            padding: '2px 6px',
                            borderRadius: 4,
                            background: 'rgba(37, 99, 235, 0.12)',
                            color: 'var(--accent-blue)',
                            border: '1px solid rgba(37, 99, 235, 0.25)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 4,
                          }}
                        >
                          <Lock size={10} />
                          Saved
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Title & Tag */}
                  <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)', marginBottom: 2 }}>
                    {p.name}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--accent-blue)', fontWeight: 600, marginBottom: 8 }}>
                    {p.tag}
                  </div>
                  <div
                    style={{
                      fontSize: 11,
                      color: 'var(--text-tertiary)',
                      lineHeight: 1.35,
                      marginBottom: 12,
                      minHeight: 30,
                    }}
                  >
                    {p.description}
                  </div>
                </div>

                {/* Bottom Badges */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 700,
                      padding: '3px 8px',
                      borderRadius: 6,
                      background: badgeStyle.bg,
                      border: `1px solid ${badgeStyle.border}`,
                      color: badgeStyle.color,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4,
                    }}
                  >
                    {p.tool_badge}
                  </span>

                  {p.last_tested && (
                    <span style={{ fontSize: 10, color: 'var(--text-tertiary)' }} title={`Last tested: ${p.last_tested}`}>
                      Tested
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Provider Configuration Workspace Panel */}
      {selectedProvider && (
        <form onSubmit={(e) => handleSaveConfig(e, false)}>
          <div className="card" style={{ padding: 24, marginBottom: 24 }}>
            {/* Header with Title and Fast Actions */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: 16,
                paddingBottom: 16,
                marginBottom: 20,
                borderBottom: '1px solid var(--border-primary)',
              }}
            >
              <div>
                <h2 style={{ fontSize: 16, fontWeight: 800, color: 'var(--text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Sliders size={18} color="var(--accent-blue)" />
                  2. Configure {selectedProvider.name}
                </h2>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                  {selectedProvider.tag} &bull; {selectedProvider.tool_badge}
                </div>
              </div>

              {/* Action Toolbar */}
              <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                {!selectedProvider.is_active && (
                  <button
                    type="button"
                    onClick={handleSetActive}
                    disabled={isActivating}
                    style={{
                      padding: '8px 16px',
                      borderRadius: 6,
                      fontSize: 12,
                      fontWeight: 700,
                      background: 'var(--bg-tertiary)',
                      color: 'var(--status-resolved)',
                      border: '1px solid var(--status-resolved)',
                      cursor: isActivating ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <Sparkles size={14} />
                    {isActivating ? 'Switching...' : 'Set as Active Provider'}
                  </button>
                )}

                {selectedProvider.has_saved_key && selectedProvider.provider_id !== 'mock' && (
                  <button
                    type="button"
                    onClick={handleDeleteKey}
                    disabled={isDeleting}
                    style={{
                      padding: '8px 14px',
                      borderRadius: 6,
                      fontSize: 12,
                      fontWeight: 600,
                      background: 'rgba(239, 68, 68, 0.08)',
                      color: 'var(--status-critical)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      cursor: isDeleting ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <Trash2 size={14} />
                    {isDeleting ? 'Removing...' : 'Remove Key'}
                  </button>
                )}
              </div>
            </div>

            {/* Inputs Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
              {/* API Key Field */}
              {selectedProvider.provider_id !== 'mock' && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-secondary)' }}>
                      API Key for {selectedProvider.name}{' '}
                      {selectedProvider.provider_id !== 'ollama' && <span style={{ color: 'var(--status-critical)' }}>*</span>}
                    </label>
                    {KEY_FORMAT_HINTS[selectedProvider.provider_id] && (
                      <a
                        href={KEY_FORMAT_HINTS[selectedProvider.provider_id].guide.replace('Get yours at ', 'https://')}
                        target="_blank"
                        rel="noreferrer"
                        style={{ fontSize: 11, color: 'var(--accent-blue)', textDecoration: 'none' }}
                      >
                        🔑 Get API Key ↗
                      </a>
                    )}
                  </div>
                  <div style={{ position: 'relative' }}>
                    <input
                      type={showKey ? 'text' : 'password'}
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder={
                        selectedProvider.has_saved_key
                          ? selectedProvider.masked_key
                          : KEY_FORMAT_HINTS[selectedProvider.provider_id]
                          ? `e.g. ${KEY_FORMAT_HINTS[selectedProvider.provider_id].example}`
                          : `Enter ${selectedProvider.name} API key...`
                      }
                      style={{
                        width: '100%',
                        padding: '10px 42px 10px 12px',
                        borderRadius: 6,
                        background: 'var(--bg-tertiary)',
                        border: getKeyFormatWarning(selectedProviderId, apiKey)
                          ? '1px solid var(--status-critical)'
                          : '1px solid var(--border-primary)',
                        color: 'var(--text-primary)',
                        fontSize: 13,
                        fontFamily: 'monospace',
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowKey(!showKey)}
                      style={{
                        position: 'absolute',
                        right: 10,
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-tertiary)',
                        cursor: 'pointer',
                      }}
                    >
                      {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>

                  {getKeyFormatWarning(selectedProviderId, apiKey) && (
                    <span style={{ fontSize: 11, color: 'var(--status-critical)', marginTop: 4, display: 'block' }}>
                      ⚠️ {getKeyFormatWarning(selectedProviderId, apiKey)}
                    </span>
                  )}

                  <span style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 4, display: 'block', lineHeight: 1.4 }}>
                    <Shield size={11} style={{ display: 'inline', marginRight: 4, color: 'var(--accent-blue)' }} />
                    <strong>Encrypted at rest.</strong> Leaving the masked placeholder intact preserves the saved key. Clear the field to remove it.
                  </span>
                </div>
              )}

              {/* Model Selection Field */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <label style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-secondary)' }}>
                    Model Identifier <span style={{ color: 'var(--status-critical)' }}>*</span>
                  </label>
                  {selectedProvider.provider_id !== 'mock' && (
                    <button
                      type="button"
                      onClick={() => setIsCustomModelMode(!isCustomModelMode)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--accent-blue)',
                        fontSize: 11,
                        fontWeight: 700,
                        cursor: 'pointer',
                        padding: '2px 6px',
                        borderRadius: 4,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4,
                      }}
                    >
                      {isCustomModelMode ? '📋 Choose from Catalog' : '✏️ Enter Custom Model'}
                    </button>
                  )}
                </div>

                {!isCustomModelMode && selectedProvider.models && selectedProvider.models.length > 0 ? (
                  <div>
                    <select
                      value={model}
                      onChange={(e) => {
                        if (e.target.value === '__enter_custom__') {
                          setIsCustomModelMode(true);
                          setModel('');
                        } else {
                          setModel(e.target.value);
                        }
                      }}
                      style={{
                        width: '100%',
                        padding: '10px 12px',
                        borderRadius: 6,
                        background: 'var(--bg-tertiary)',
                        border: '1px solid var(--border-primary)',
                        color: 'var(--text-primary)',
                        fontSize: 13,
                        fontFamily: 'monospace',
                        cursor: 'pointer',
                      }}
                    >
                      {selectedProvider.models.map((m) => (
                        <option key={m} value={m}>
                          {m} {m === selectedProvider.default_model ? '(Recommended)' : ''}
                        </option>
                      ))}
                      {selectedProvider.provider_id !== 'mock' && (
                        <option value="__enter_custom__">➕ Enter custom model identifier...</option>
                      )}
                    </select>
                    <span style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 4, display: 'block' }}>
                      Recommended catalog models. Click &quot;Enter Custom Model&quot; to specify any custom or fine-tuned model ID.
                    </span>
                  </div>
                ) : (
                  <div>
                    <input
                      type="text"
                      value={model}
                      onChange={(e) => setModel(e.target.value)}
                      placeholder={
                        selectedProvider.provider_id === 'openai'
                          ? 'e.g. gpt-4.5-preview, ft:gpt-4o:my-org:custom-123'
                          : selectedProvider.provider_id === 'claude'
                          ? 'e.g. claude-3-7-sonnet-20250219'
                          : selectedProvider.provider_id === 'gemini'
                          ? 'e.g. gemini-2.5-pro, gemini-2.0-flash-exp'
                          : selectedProvider.provider_id === 'groq'
                          ? 'e.g. deepseek-r1-distill-llama-70b, llama-3.3-70b-specdec'
                          : selectedProvider.default_model || 'e.g. meta-llama/Llama-3.3-70B-Instruct'
                      }
                      style={{
                        width: '100%',
                        padding: '10px 12px',
                        borderRadius: 6,
                        background: 'var(--bg-tertiary)',
                        border: '1px solid var(--border-primary)',
                        color: 'var(--text-primary)',
                        fontSize: 13,
                        fontFamily: 'monospace',
                      }}
                    />
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
                      <span style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>
                        Supports any standard, newly released, or fine-tuned model ID for {selectedProvider.name}.
                      </span>
                      {selectedProvider.models && selectedProvider.models.length > 0 && selectedProvider.provider_id !== 'mock' && (
                        <button
                          type="button"
                          onClick={() => {
                            setIsCustomModelMode(false);
                            setModel(selectedProvider.default_model || selectedProvider.models[0] || '');
                          }}
                          style={{
                            background: 'none',
                            border: 'none',
                            color: 'var(--accent-blue)',
                            fontSize: 11,
                            cursor: 'pointer',
                            textDecoration: 'underline',
                          }}
                        >
                          Reset to Catalog
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Base URL (Optional for Ollama / Custom / OpenRouter) */}
              {(selectedProvider.provider_id === 'ollama' ||
                selectedProvider.provider_id === 'openrouter' ||
                selectedProvider.provider_id === 'huggingface') && (
                <div>
                  <label style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                    Custom Base Endpoint URL (Optional)
                  </label>
                  <input
                    type="text"
                    value={baseUrl}
                    onChange={(e) => setBaseUrl(e.target.value)}
                    placeholder={
                      selectedProvider.provider_id === 'ollama'
                        ? 'http://localhost:11434/v1'
                        : 'https://openrouter.ai/api/v1'
                    }
                    style={{
                      width: '100%',
                      padding: '10px 12px',
                      borderRadius: 6,
                      background: 'var(--bg-tertiary)',
                      border: '1px solid var(--border-primary)',
                      color: 'var(--text-primary)',
                      fontSize: 13,
                      fontFamily: 'monospace',
                    }}
                  />
                  <span style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 4, display: 'block' }}>
                    Leave empty to use provider's standard official endpoint.
                  </span>
                </div>
              )}

              {/* Temperature Slider */}
              <div>
                <label style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                  Reasoning Temperature: <strong style={{ color: 'var(--accent-blue)' }}>{temperature.toFixed(2)}</strong>
                </label>
                <input
                  type="range"
                  min="0.0"
                  max="0.5"
                  step="0.05"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  style={{ width: '100%', cursor: 'pointer', accentColor: 'var(--accent-blue)' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-tertiary)', marginTop: 2 }}>
                  <span>0.0 (Strict / Deterministic)</span>
                  <span>0.5 (Analytical Reasoning)</span>
                </div>
              </div>
            </div>

            {/* 3. Live API Connectivity Test Box */}
            <div
              style={{
                marginTop: 24,
                padding: 18,
                borderRadius: 8,
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-primary)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
                <div>
                  <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Zap size={15} color="var(--accent-teal)" />
                    3. Diagnostic API Connectivity Test
                  </h3>
                  <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
                    Lightweight ping prompt (&quot;Reply with OK.&quot;) with 10.0s timeout. Verifies credentials without altering active provider.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handleTestConnection}
                  disabled={isTesting || cooldown > 0}
                  style={{
                    padding: '9px 18px',
                    borderRadius: 6,
                    fontSize: 12,
                    fontWeight: 700,
                    background: cooldown > 0 ? 'var(--bg-secondary)' : 'var(--bg-elevated)',
                    color: cooldown > 0 ? 'var(--text-tertiary)' : 'var(--accent-blue)',
                    border: `1px solid ${cooldown > 0 ? 'var(--border-primary)' : 'var(--accent-blue)'}`,
                    cursor: isTesting || cooldown > 0 ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    transition: 'all 0.15s ease',
                  }}
                >
                  {isTesting ? (
                    <>
                      <RefreshCw size={14} className="animate-spin" />
                      Testing API Key...
                    </>
                  ) : cooldown > 0 ? (
                    <>
                      <Clock size={14} />
                      Cooldown ({cooldown}s)
                    </>
                  ) : (
                    <>
                      <Activity size={14} />
                      Test API Key
                    </>
                  )}
                </button>
              </div>

              {/* Test Results Display */}
              {testResult && (
                <div
                  className="animate-fade-in"
                  style={{
                    marginTop: 14,
                    padding: 14,
                    borderRadius: 6,
                    background: testResult.status === 'success' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
                    border: `1px solid ${testResult.status === 'success' ? 'var(--status-resolved)' : 'var(--status-critical)'}`,
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <span
                      style={{
                        fontSize: 13,
                        fontWeight: 700,
                        color: testResult.status === 'success' ? 'var(--status-resolved)' : 'var(--status-critical)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                      }}
                    >
                      {testResult.status === 'success' ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
                      {testResult.status === 'success'
                        ? 'Diagnostic Ping Verified'
                        : `API Diagnostic Error (${testResult.category || 'failure'})`}
                    </span>

                    {testResult.latency_ms > 0 && (
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: 12,
                          background: 'rgba(37, 99, 235, 0.15)',
                          color: 'var(--accent-blue)',
                        }}
                      >
                        ⚡ Latency: {testResult.latency_ms} ms
                      </span>
                    )}
                  </div>

                  <div style={{ fontSize: 12, color: 'var(--text-primary)', lineHeight: 1.45, marginTop: 4 }}>
                    {testResult.message}
                  </div>

                  {testResult.discovered_models && testResult.discovered_models.length > 0 && (
                    <div style={{ fontSize: 11, color: 'var(--accent-teal)', marginTop: 6, fontWeight: 600 }}>
                      ✓ Dynamically discovered and cached {testResult.discovered_models.length} live models from provider catalog.
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Bottom Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
              <button
                type="submit"
                disabled={isSaving}
                style={{
                  padding: '11px 22px',
                  borderRadius: 6,
                  fontSize: 13,
                  fontWeight: 700,
                  background: 'var(--bg-elevated)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border-secondary)',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  transition: 'all 0.15s ease',
                }}
              >
                {isSaving ? <RefreshCw size={15} className="animate-spin" /> : <Save size={15} />}
                Save Configuration
              </button>

              <button
                type="button"
                onClick={(e) => handleSaveConfig(e, true)}
                disabled={isSaving}
                style={{
                  padding: '11px 26px',
                  borderRadius: 6,
                  fontSize: 13,
                  fontWeight: 700,
                  background: 'var(--accent-blue)',
                  color: '#ffffff',
                  border: 'none',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  boxShadow: '0 0 16px rgba(37, 99, 235, 0.4)',
                  transition: 'all 0.15s ease',
                }}
              >
                {isSaving ? <RefreshCw size={15} className="animate-spin" /> : <Sparkles size={15} />}
                Save &amp; Activate
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
};

export default Settings;
