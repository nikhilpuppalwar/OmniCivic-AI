# OmniCivic AI — Design System & UI/UX Specification

---

## 1. Design Philosophy & Visual Identity

OmniCivic AI is engineered to deliver an **ultra-premium, command-center aesthetic** suitable for high-stakes municipal operations. The UI blends sleek dark-mode glassmorphism, dynamic glowing status indicators, vibrant categorical badges, and real-time micro-animations to instantly convey complex multi-agent intelligence.

---

## 2. Color Palette & Design Tokens

### 2.1 Dark Mode Theme Tokens

```css
:root {
  /* Surface & Background Colors */
  --bg-dark: #0b0f19;
  --bg-card: rgba(17, 24, 39, 0.85);
  --bg-card-hover: rgba(31, 41, 55, 0.9);
  --border-glass: rgba(255, 255, 255, 0.1);
  --border-glass-glow: rgba(59, 130, 246, 0.3);

  /* Brand Accents */
  --accent-blue: #3b82f6;
  --accent-cyan: #06b6d4;
  --accent-indigo: #6366f1;

  /* Priority & Status Colors */
  --status-critical: #ef4444; /* Glowing Red */
  --status-high: #f97316;     /* Vivid Orange */
  --status-medium: #eab308;   /* Amber Yellow */
  --status-low: #10b981;      /* Emerald Green */
  --status-resolved: #10b981; /* Emerald Green */
  --status-escalated: #a855f7;/* Imperial Purple */

  /* Typography Colors */
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;
}
```

---

## 3. Component Architecture & Visual Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Header / Navigation                              │
├───────────────────────────────┬─────────────────────────────────────────────┤
│   Citizen Reports Feed (Left) │           Active Incident Display           │
│  ┌─────────────────────────┐  │  ┌───────────────────────────────────────┐  │
│  │ Report Card CIV-1001    │  │  │ Agent Pipeline Progress Indicator     │  │
│  │ [Run Agentic AI Button] │  │  └───────────────────────────────────────┘  │
│  └─────────────────────────┘  │  ┌───────────────────────────────────────┐  │
│  ┌─────────────────────────┐  │  │ Root Cause Card (Hypothesis)         │  │
│  │ Report Card CIV-1002    │  │  └───────────────────────────────────────┘  │
│  └─────────────────────────┘  │  ┌───────────────────┬───────────────────┐  │
│                               │  │ Civic Impact      │ Sequenced Plan    │  │
│                               │  │ Priority Gauge    │ (Approve Button)  │  │
│                               │  └───────────────────┴───────────────────┘  │
│                               │  ┌───────────────────────────────────────┐  │
│                               │  │ Verification & Anti-Fraud Card        │  │
│                               │  └───────────────────────────────────────┘  │
└───────────────────────────────┴─────────────────────────────────────────────┘
```

---

## 4. Key UI Components & Micro-Interactions

### 4.1 Agent Pipeline Tracker (`AgentPipeline.tsx`)
- Displays all 7 stages horizontally: `Perception` $\to$ `Clustering` $\to$ `Detection` $\to$ `Root Cause` $\to$ `Impact` $\to$ `Response` $\to$ `Filing`.
- Active stage animates with a pulsing blue glow ring and spinner icon.
- Completed stages transition smoothly to an emerald green checkmark badge (`✓`).

### 4.2 Civic Impact Gauge (`ImpactGauge.tsx`)
- Renders a semi-circular gauge displaying the 0-100 score.
- Dynamic color transitions based on priority score ($S \ge 80$ Red, $S \ge 65$ Orange, $S \ge 45$ Yellow, $S < 45$ Green).
- Interactive expander reveals the 6-factor weight breakdown table.

### 4.3 Root Cause Card (`RootCauseCard.tsx`)
- Features a dark glassmorphic container with a subtle indigo border glow.
- Displays the causal chain (e.g., `Water Leak` $\to$ `Road Damage` $\to$ `Pothole` $\to$ `Waterlogging`) connected with arrow badges.
- Prominently displays the safety disclaimer badge:
  > *"AI-generated civic incident hypothesis. Physical inspection recommended."*

### 4.4 Response Plan Card (`ResponsePlanCard.tsx`)
- Displays numbered execution steps with clear department badges (`WATER_BOARD`, `ROADS_DEPT`, `STORM_WATER_DRAINAGE`).
- Shows step dependencies (e.g., *"Step 2 depends on Step 1 completion"*).
- Includes the primary **Approve Multi-Department Plan** CTA button with hover elevation.

### 4.5 Verification Card (`VerificationCard.tsx`)
- Displays side-by-side "Before" and "After" photos with photo comparison overlays.
- Displays verification state badges:
  - `LOCATION_MISMATCH` (Red alert badge with distance indicator e.g. `142m > 100m limit`).
  - `RESOLUTION_VERIFIED` (Green success badge with confidence score e.g. `95%`).

---

## 5. Micro-Animations & CSS Glassmorphism Rules

1. **Glassmorphism Backdrop Filter:**
   ```css
   background: var(--bg-card);
   backdrop-filter: blur(12px);
   border: 1px solid var(--border-glass);
   box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
   ```

2. **Hover Elevation & Border Glow:**
   ```css
   transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

   .card:hover {
     transform: translateY(-2px);
     border-color: var(--border-glass-glow);
     box-shadow: 0 12px 40px 0 rgba(59, 130, 246, 0.15);
   }
   ```

3. **Status Pulse Animation:**
   ```css
   @keyframes pulse-glow {
     0%, 100% { opacity: 1; transform: scale(1); }
     50% { opacity: 0.6; transform: scale(1.05); }
   }
   .status-pulse {
     animation: pulse-glow 2s infinite ease-in-out;
   }
   ```
