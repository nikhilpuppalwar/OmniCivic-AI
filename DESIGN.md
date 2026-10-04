# OmniCivic AI — Design System & UI/UX Specification

---

## 1. Design Philosophy & Visual Identity

OmniCivic AI is crafted as an **ultra-premium municipal command center** engineered for high-stakes urban infrastructure operations. The user interface harmonizes modern glassmorphism, dynamic data visualizations, color-coded priority cues, interactive spatial GIS mapping, and subtle micro-animations to instantly transform raw civic noise into actionable intelligence.

The system features seamless **Dark & Light Mode** support powered by CSS custom properties and persistent theme state stored in browser `localStorage`.

---

## 2. Color Palette & Design Tokens

### 2.1 Dark & Light Theme Variables (`index.css`)

```css
:root {
  /* Dark Theme Tokens (Default) */
  --bg-primary: #0A0D14;
  --bg-secondary: #0F1420;
  --bg-tertiary: #161D2E;
  --bg-card: rgba(15, 20, 32, 0.88);
  --border-primary: #1E283D;
  --border-secondary: #2A3650;
  --border-glass-glow: rgba(59, 130, 246, 0.35);

  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --text-tertiary: #64748B;

  /* Brand Accents */
  --accent-blue: #2563EB;
  --accent-blue-hover: #1D4ED8;
  --accent-teal: #0D9488;
  --accent-indigo: #6366F1;

  /* Priority & Status Signals */
  --status-critical: #EF4444;      /* Glowing Red - Emergency / Immediate Hazard */
  --status-critical-bg: rgba(239, 68, 68, 0.12);
  --status-high: #F59E0B;          /* Vivid Amber - High Priority / Attention */
  --status-high-bg: rgba(245, 158, 11, 0.12);
  --status-medium: #3B82F6;        /* Cobalt Blue - Standard Queue */
  --status-medium-bg: rgba(59, 130, 246, 0.12);
  --status-low: #64748B;           /* Slate - Minor / Routine */
  --status-low-bg: rgba(100, 116, 139, 0.12);
  --status-resolved: #10B981;      /* Emerald Green - Verified Closure */
  --status-resolved-bg: rgba(16, 185, 129, 0.12);
  --status-escalated: #A855F7;     /* Purple Pulse - SLA Breach */
  --status-escalated-bg: rgba(168, 85, 247, 0.12);
}

[data-theme="light"] {
  /* Light Theme Tokens */
  --bg-primary: #F8FAFC;
  --bg-secondary: #FFFFFF;
  --bg-tertiary: #F1F5F9;
  --bg-card: rgba(255, 255, 255, 0.95);
  --border-primary: #E2E8F0;
  --border-secondary: #CBD5E1;
  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-tertiary: #94A3B8;
}
```

---

## 3. Application Layout Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Header: [Logo] OmniCivic AI | [Dashboard] [Citizen Portal] [AI Settings]  │
│         [● AI Engine Operational] [☀️/🌙 Theme Toggle]                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Aggregate Stats Row: Total Reports | Incidents | Critical | Resolved | SLA │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ Spatial Intelligence & Feeds  │ Active Incident Workspace                   │
│ [List View | Map View Toggle] │ ┌─────────────────────────────────────────┐ │
│ ┌───────────────────────────┐ │ │ Multi-Agent Reasoning Pipeline (7-Stage)│ │
│ │ • Leaflet Spatial Map OR  │ │ └─────────────────────────────────────────┘ │
│ │ • Incident Intelligence   │ │ ┌─────────────────────────────────────────┐ │
│ │   Feed Cards              │ │ │ Geo-Temporal Cluster & Evidence Gallery │ │
│ │ • Citizen Reports Feed    │ │ └─────────────────────────────────────────┘ │
│ │   [Run Agentic AI]        │ │ ┌───────────────────┬─────────────────────┐ │
│ └───────────────────────────┘ │ │ Civic Impact      │ Root Cause Card     │ │
│                               │ │ 0-100 Gauge       │ Hypothesis & Tools  │ │
│                               │ └───────────────────┴─────────────────────┘ │
│                               │ ┌───────────────────┬─────────────────────┐ │
│                               │ │ Sequenced Plan    │ Resolution Panel    │ │
│                               │ │ [Approve Button]  │ Verification Beat   │ │
│                               │ └───────────────────┴─────────────────────┘ │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

---

## 4. Key UI Components & Interactions

### 4.1 Navigation Bar & Operational Indicator
- Sticky glassmorphic top navigation with route tabs: **Operations Dashboard** (`/`), **Citizen Portal** (`/report`), and **AI Settings** (`/settings`).
- Live system status pill (`AI Engine Operational`) featuring a pulsing emerald beacon.
- Theme switch toggle smoothly toggling between dark command center and crisp daylight mode.

### 4.2 Spatial Map View (`MapView.tsx`)
- Powered by **Leaflet** & **React-Leaflet** with theme-responsive tile layers:
  - *Dark Mode:* CartoDB Dark Matter (`https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`)
  - *Light Mode:* CartoDB Positron (`https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png`)
- **Cluster Radius Circles:** Translucent circular overlays displaying the spatial bounding radius (e.g. 150m) with glowing boundary strokes.
- **Custom HTML DivIcon Pins:** Color-coded pins matching incident priority with subtle bounce on selection.
- **Sensitive Sites Overlay:** Displays nearby schools, hospitals, and clinics discovered via OpenStreetMap Overpass with distance badges.
- **Auto-Recenter & Tile Bounds Invalidation:** Smoothly pans to selected incidents and recalculates bounding dimensions upon tab changes.

### 4.3 Multi-Agent Reasoning Pipeline (`AgentPipeline.tsx`)
- Visualizes 7 core pipeline stages: `Perception` $\to$ `Clustering` $\to$ `Detection` $\to$ `Root Cause` $\to$ `Impact` $\to$ `Response` $\to$ `Filing`.
- Active executing stage highlights with a cobalt glow ring and spinning loader.
- Completed stages reveal emerald checkmark badges with stage output previews and confidence ratings.
- Integrated progress percentage bar transitioning from 0% to 100%.

### 4.4 Root Cause Investigation Card (`RootCauseCard.tsx`)
- Displays reasoning execution mode badge: **AI Agentic** (emerald badge) vs **Deterministic Fallback** (amber badge).
- **Tool Badges:** Interactive tags indicating tools invoked during analysis (`🌧️ Weather checked`, `🏫 Nearby sites checked`, `📊 Dependency graph`, `📜 Historical incidents`, `📏 Distance verified`).
- **Interactive Causal Chain:** Visual node sequence highlighting the root origin in glowing crimson (e.g., `WATER_LEAKAGE` $\to$ `ROAD_DAMAGE` $\to$ `POTHOLE` $\to$ `WATERLOGGING`).
- Mandatory civic hypothesis safety disclaimer with alert icon.

### 4.5 Civic Impact Priority Gauge (`ImpactGauge.tsx`)
- Semi-circular SVG gauge with smooth needle rotation based on score $S \in [0, 100]$.
- Priority badge transitions dynamically between `CRITICAL` ($S \ge 80$), `HIGH` ($S \ge 65$), `MEDIUM` ($S \ge 45$), and `LOW` ($S < 45$).
- Expandable 6-factor weight breakdown detailing severity, proximity, population affected, duration, repeat complaints, and secondary risks.

### 4.6 Multi-Department Response Plan (`ResponsePlan.tsx`)
- Sequenced work order cards displaying assigned municipal department, estimated repair hours, and prerequisite dependencies.
- Prevents paving over un-repaired underground leaks through topological validation.
- Prominent **Approve Multi-Department Plan** CTA button transitioning incident status to `ACTION_IN_PROGRESS`.

### 4.7 Resolution Verification & Anti-Fraud Panel (`ResolutionPanel.tsx`)
- Designed for rehearsed demonstrations with 1-click presets:
  - **Attempt 1: Mismatched Photo** (`resolved_leak_wrong.jpg` at distant GPS): Triggers red `LOCATION_MISMATCH` alert banner ($>100\text{m}$).
  - **Attempt 2: Correct Evidence** (`resolved_leak_correct.jpg` at Chakala Junction): Triggers emerald `RESOLUTION_VERIFIED` banner and resolves ticket.

### 4.8 AI Settings & Multi-Provider Manager (`Settings.tsx`)
- Dedicated interface for configuring LLM providers: **Groq**, **OpenAI**, **Anthropic Claude**, **Google Gemini**, **Hugging Face**, **OpenRouter**, **Ollama**, and **Deterministic Simulation**.
- 1-click **Authorize Dev Token** button to authenticate with the backend operator token.
- Provider cards showing model selection, tool capability badges (`✓ Tool Calling` vs `⚠️ Limited Tool Support`), temperature slider, and custom base URL inputs.
- In-flight **Test Connection** button executing a live 10-second ping test with round-trip latency display in milliseconds.

---

## 5. Micro-Animations & Glassmorphism Styling

```css
/* Glassmorphism Surface Container */
.card {
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  border-color: var(--border-glass-glow);
  box-shadow: 0 8px 30px rgba(37, 99, 235, 0.12);
}

/* Pulsing Status Badges */
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.15); }
}

.animate-pulse {
  animation: pulse-dot 1.8s infinite ease-in-out;
}
```

