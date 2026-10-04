export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface Location {
  latitude: number;
  longitude: number;
  address: string;
  ward: string;
}

export interface CivicReport {
  report_id: string;
  timestamp: string;
  citizen_name: string;
  phone: string;
  location: Location;
  description: string;
  image_filename: string;
  status: string;
  linked_incident_id: string | null;
  ward: string;
  scenario_id: number | null;
}

export interface PerceptionResult {
  report_id: string;
  issue_type: string;
  severity: string;
  confidence: number;
  evidence_text: string;
  image_filename: string;
  visual_evidence?: string[];
}

export interface ImpactBreakdown {
  severity_score: number;
  infrastructure_proximity: number;
  people_affected: number;
  duration: number;
  repeat_reports: number;
  secondary_risk: number;
}

export interface ResponseStep {
  step_number: number;
  department: string;
  department_name: string;
  action: string;
  reason: string;
  estimated_hours: number;
  depends_on: string[];
  resources: string[];
  issues: string[];
}

export interface AgentLogEntry {
  timestamp: string;
  agent: string;
  message: string;
  decision: string;
  evidence_used: string[];
  confidence: number;
  recommended_action: string;
}

export interface SensitiveSite {
  id?: string;
  name: string;
  type: string;
  latitude?: number;
  longitude?: number;
  lat?: number;
  lon?: number;
  distance_m?: number;
}

export interface AgentTraceStep {
  step: number;
  type: 'model_call' | 'tool_call' | 'tool_result' | 'final' | 'deterministic' | 'single_turn' | string;
  tool?: string;
  tool_name?: string;
  args?: Record<string, unknown>;
  arguments?: Record<string, unknown>;
  result?: Record<string, unknown> | string;
  result_summary?: string;
  latency_ms?: number;
  summary?: string;
  error?: string | null;
  timestamp?: string;
}

export interface ReflectionCheck {
  name: string;
  passed: boolean;
  detail: string;
}

export interface ReflectionMetadata {
  verdict: 'approved' | 'revised' | 'unresolved' | string;
  iterations: number;
  issues?: string[];
  checks: ReflectionCheck[];
  pass_count?: number;
  fail_count?: number;
  revised?: boolean;
  revisions_applied?: string[];
}

export interface IncidentContext {
  incident_id: string;
  status: string;
  classification: string;
  reasoning_mode?: 'agentic_multi_turn' | 'single_turn_enriched' | 'deterministic_fallback' | string;
  tools_used?: string[];
  tool_traces?: Array<{ tool_name: string; args: Record<string, unknown>; result: Record<string, unknown>; latency_ms: number }>;
  agent_trace?: AgentTraceStep[];
  reflection?: ReflectionMetadata;
  nearby_sites?: SensitiveSite[];
  created_at: string;
  updated_at: string;
  connected_reports: string[];
  cluster: {
    radius_m: number;
    time_window_days: number;
    center_lat: number;
    center_lon: number;
    report_count: number;
  };
  perception_results: PerceptionResult[];
  root_cause: {
    hypothesis: string;
    confidence: number;
    evidence: string[];
    chain: string[];
    disclaimer: string;
    tools_used?: string[];
    reasoning_notes?: string;
    nearby_sites?: SensitiveSite[];
  };

  impact_score: {
    score: number;
    priority: string;
    breakdown: ImpactBreakdown;
    explanation: string;
  };
  response_plan: {
    steps: ResponseStep[];
    rationale: string;
    approved: boolean;
    approved_by: string;
    approved_at: string;
  };
  resolution: {
    before_photo: string;
    after_photo: string;
    verification_result: string;
    verification_details: string;
    confidence: number;
    requested_evidence?: string[];
  };
  sla: {
    deadline: string;
    reminders_sent: number;
    escalated: boolean;
    escalation_reason: string;
  };
}


export interface PipelineStage {
  status: string;
  result: Record<string, unknown>;
}

export interface PipelineResult {
  report_id: string;
  incident_id: string | null;
  stages: Record<string, PipelineStage>;
  agent_logs: AgentLogEntry[];
}

export interface DashboardStats {
  total_reports: number;
  total_incidents: number;
  active_incidents: number;
  critical_incidents: number;
  resolved_incidents: number;
  reopened_incidents: number;
  escalated_incidents: number;
}

export type ToolSupportType = 'TOOL_CALLING_SUPPORTED' | 'LIMITED_TOOL_SUPPORT' | 'NO_TOOL_SUPPORT';

export interface ProviderConfig {
  provider_id: string;
  name: string;
  tag: string;
  description: string;
  tool_support: ToolSupportType;
  tool_badge: string;
  default_model: string;
  models: string[];
  allows_custom_model: boolean;
  is_active: boolean;
  has_saved_key: boolean;
  masked_key: string;
  selected_model: string;
  temperature: number;
  base_url: string;
  last_tested: string;
  last_test_status: string;
}

export interface PublicSettingsPayload {
  active_provider: string;
  active_model: string;
  providers: ProviderConfig[];
}

export interface ProviderSavePayload {
  provider_id: string;
  api_key?: string;
  model?: string;
  base_url?: string;
  temperature?: number;
  set_active?: boolean;
}

export interface LLMSettings {
  provider: string;
  api_key?: string;
  api_key_masked?: string;
  model?: string;
  base_url?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface LLMTestResult {
  status: 'success' | 'error';
  category?: string;
  message: string;
  latency_ms: number;
  provider: string;
  model: string;
  discovered_models?: string[];
}

// ── Operator Token Helpers ──────────────────────────────────────────────────

export const OPERATOR_TOKEN_STORAGE_KEY = 'omnicivic_operator_token';

export function getStoredOperatorToken(): string {
  try {
    return localStorage.getItem(OPERATOR_TOKEN_STORAGE_KEY) || '';
  } catch {
    return '';
  }
}

export function setStoredOperatorToken(token: string): void {
  try {
    if (token && token.trim()) {
      localStorage.setItem(OPERATOR_TOKEN_STORAGE_KEY, token.trim());
    } else {
      localStorage.removeItem(OPERATOR_TOKEN_STORAGE_KEY);
    }
  } catch {
    // Ignore localStorage access failures
  }
}

// ── API Functions ─────────────────────────────────────────────────────────

async function fetchJson(url: string, options?: RequestInit) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string> || {}),
  };
  const token = getStoredOperatorToken();
  if (token) {
    headers['X-Operator-Token'] = token;
  }

  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    const err: any = new Error(error.detail || res.statusText);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

export const api = {
  submitReport: (data: {
    citizen_name?: string;
    phone?: string;
    latitude: number;
    longitude: number;
    address?: string;
    ward?: string;
    description: string;
    image_filename?: string;
    image_file?: File | null;
  }) => {
    const formData = new FormData();
    if (data.citizen_name) formData.append('citizen_name', data.citizen_name);
    if (data.phone) formData.append('phone', data.phone);
    formData.append('latitude', String(data.latitude));
    formData.append('longitude', String(data.longitude));
    if (data.address) formData.append('location_name', data.address);
    if (data.ward) formData.append('ward', data.ward);
    formData.append('description', data.description);
    if (data.image_filename) formData.append('image_filename', data.image_filename);
    if (data.image_file) formData.append('image', data.image_file);

    return fetch(`${API_BASE}/reports`, {
      method: 'POST',
      body: formData,
    }).then(async (res) => {
      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || res.statusText);
      }
      return res.json();
    });
  },

  getReports: () => fetchJson('/reports'),
  getReport: (id: string) => fetchJson(`/reports/${id}`),

  // Analysis
  analyzeReport: (id: string): Promise<PipelineResult> =>
    fetchJson(`/analyze/${id}`, { method: 'POST' }),

  // Incidents
  getIncidents: () => fetchJson('/incidents'),
  getIncident: (id: string): Promise<IncidentContext> => fetchJson(`/incidents/${id}`),
  getImpact: (id: string) => fetchJson(`/incidents/${id}/impact`),
  getResponsePlan: (id: string) => fetchJson(`/incidents/${id}/response-plan`),

  approvePlan: (id: string) => fetchJson(`/incidents/${id}/approve-plan`, { method: 'POST' }),

  // Resolution
  submitResolution: (id: string, data: {
    after_photo: string;
    after_latitude: number;
    after_longitude: number;
    notes?: string;
  }) => fetchJson(`/incidents/${id}/resolution`, { method: 'POST', body: JSON.stringify(data) }),

  verifyResolution: (id: string) =>
    fetchJson(`/incidents/${id}/verify-resolution`, { method: 'POST' }),

  // Escalation
  advanceDemoTime: (id: string, hours: number = 72) =>
    fetchJson(`/incidents/${id}/advance-demo-time`, {
      method: 'POST',
      body: JSON.stringify({ hours }),
    }),

  // Dashboard & Logs
  getStats: (): Promise<DashboardStats> => fetchJson('/dashboard/stats'),
  getAgentLogs: () => fetchJson('/agent-logs'),

  // Settings (Multi-Provider)
  getDevOperatorToken: (): Promise<{ token: string }> => fetchJson('/api/settings/dev-token'),
  getSettings: (): Promise<PublicSettingsPayload> => fetchJson('/api/settings'),
  saveProviderSettings: (data: ProviderSavePayload): Promise<{ message: string; settings: PublicSettingsPayload }> =>
    fetchJson('/api/settings', { method: 'POST', body: JSON.stringify(data) }),
  saveSettings: (settings: any) =>
    fetchJson('/api/settings', { method: 'POST', body: JSON.stringify(settings) }),
  setActiveProvider: (provider_id: string): Promise<{ message: string; settings: PublicSettingsPayload }> =>
    fetchJson('/api/settings/set-active', { method: 'POST', body: JSON.stringify({ provider_id }) }),
  deleteProvider: (provider_id: string): Promise<{ message: string; settings: PublicSettingsPayload }> =>
    fetchJson(`/api/settings/provider/${provider_id}`, { method: 'DELETE' }),
  testSettings: (settings: { provider: string; api_key?: string; model?: string; base_url?: string }): Promise<LLMTestResult> =>
    fetchJson('/api/settings/test', { method: 'POST', body: JSON.stringify(settings) }),

  // Dev
  resetDemo: () => fetchJson('/dev/reset-demo', { method: 'POST' }),
  getScenarios: () => fetchJson('/dev/scenarios'),
  getSeedImages: () => fetchJson('/dev/seed-images'),
  getPerceptionLookup: () => fetchJson('/dev/perception-lookup'),

  // Geocoding Proxy (OSM Nominatim)
  geocode: (q: string): Promise<GeocodeResponse> =>
    fetchJson(`/geocode?q=${encodeURIComponent(q)}`),
};

export interface GeocodeResult {
  display_name: string;
  latitude: number;
  longitude: number;
  type: string;
  importance: number;
  ward?: string;
}

export interface GeocodeResponse {
  query: string;
  results: GeocodeResult[];
  count: number;
}

