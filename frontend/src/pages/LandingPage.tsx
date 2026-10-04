import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, type DashboardStats } from '../lib/api';
import {
  Activity,
  ArrowRight,
  ShieldCheck,
  Cpu,
  MapPin,
  Sparkles,
  FileCheck2,
  Workflow,
  Compass,
  CloudRain,
  School,
  Lock,
  ChevronRight,
  Play,
  RotateCcw,
} from 'lucide-react';

import groqLogo from '../assets/groq.png';
import openaiLogo from '../assets/openai.svg';
import claudeLogo from '../assets/claude-color.svg';
import geminiLogo from '../assets/gemini-color.svg';
import ollamaLogo from '../assets/ollama.svg';

export default function LandingPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    total_reports: 0,
    total_incidents: 0,
    active_incidents: 0,
    critical_incidents: 0,
    resolved_incidents: 0,
    reopened_incidents: 0,
    escalated_incidents: 0,
  });
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    api.getStats()
      .then((data) => {
        setStats(data);
        setLoadingStats(false);
      })
      .catch((err) => {
        console.error('Failed to load stats on landing page:', err);
        setLoadingStats(false);
      });
  }, []);

  const handleLaunchScenario = (reportId: string) => {
    navigate('/dashboard', { state: { autoAnalyzeId: reportId } });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 64, paddingBottom: 48, maxWidth: 1240, margin: '0 auto' }}>
      
      {/* ── 1. HERO SECTION ──────────────────────────────────────────────── */}
      <section style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        paddingTop: 36,
        paddingBottom: 24,
      }}>
        {/* Top Intelligence Badge */}
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          padding: '6px 14px',
          borderRadius: 24,
          background: 'rgba(37, 99, 235, 0.1)',
          border: '1px solid rgba(37, 99, 235, 0.25)',
          color: 'var(--accent-blue)',
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: '0.04em',
          textTransform: 'uppercase',
          marginBottom: 20,
        }}>
          <Sparkles size={14} color="var(--accent-blue)" />
          Autonomous Civic Incident Intelligence System
        </div>

        {/* Framing Headline & Tagline */}
        <h1 style={{
          fontSize: 'clamp(32px, 5vw, 54px)',
          fontWeight: 900,
          lineHeight: 1.15,
          letterSpacing: '-0.03em',
          color: 'var(--text-primary)',
          maxWidth: 920,
          marginBottom: 16,
        }}>
          Different complaints.{' '}
          <span style={{
            background: 'linear-gradient(135deg, #2563EB 0%, #0D9488 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            One hidden signal.
          </span>
        </h1>

        <p style={{
          fontSize: 'clamp(15px, 2vw, 18px)',
          color: 'var(--text-secondary)',
          lineHeight: 1.6,
          maxWidth: 780,
          margin: '0 auto 32px',
        }}>
          Cities don't have a shortage of complaints — they have a shortage of intelligence connecting them. OmniCivic AI correlates independent citizen reports across space and time to expose cascading infrastructure failures, prioritize public threats, and prevent costly re-repair cycles.
        </p>

        {/* Primary Action CTAs */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 14, justifyContent: 'center', marginBottom: 40 }}>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-primary"
            style={{
              padding: '12px 24px',
              fontSize: 15,
              fontWeight: 700,
              borderRadius: 8,
              boxShadow: '0 0 20px rgba(37, 99, 235, 0.4)',
              display: 'flex',
              alignItems: 'center',
              gap: 10,
            }}
          >
            <Activity size={18} />
            Launch Operations Dashboard
            <ArrowRight size={16} />
          </button>

          <button
            onClick={() => navigate('/report')}
            className="btn btn-secondary"
            style={{
              padding: '12px 22px',
              fontSize: 15,
              fontWeight: 600,
              borderRadius: 8,
              background: 'var(--bg-tertiary)',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <MapPin size={18} color="var(--accent-teal)" />
            Submit Citizen Grievance
          </button>

          <button
            onClick={() => navigate('/settings')}
            className="btn btn-secondary"
            style={{
              padding: '12px 20px',
              fontSize: 15,
              fontWeight: 600,
              borderRadius: 8,
              background: 'transparent',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <Cpu size={18} color="var(--text-secondary)" />
            AI Model Settings
          </button>
        </div>

        {/* Live System Metrics Strip */}
        <div style={{
          width: '100%',
          maxWidth: 960,
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-primary)',
          borderRadius: 12,
          padding: '16px 24px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: 16,
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.1)',
        }}>
          <div>
            <span style={{ fontSize: 11, color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              Grievance Reports
            </span>
            <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-primary)', marginTop: 2 }}>
              {loadingStats ? '...' : stats.total_reports}
            </div>
          </div>

          <div>
            <span style={{ fontSize: 11, color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              Correlated Incidents
            </span>
            <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--accent-blue)', marginTop: 2 }}>
              {loadingStats ? '...' : stats.total_incidents}
            </div>
          </div>

          <div>
            <span style={{ fontSize: 11, color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              Critical Safety Hazards
            </span>
            <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--status-critical)', marginTop: 2 }}>
              {loadingStats ? '...' : stats.critical_incidents}
            </div>
          </div>

          <div>
            <span style={{ fontSize: 11, color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              Verified Resolved
            </span>
            <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--status-resolved)', marginTop: 2 }}>
              {loadingStats ? '...' : stats.resolved_incidents}
            </div>
          </div>

          <div>
            <span style={{ fontSize: 11, color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              SLA Escalations
            </span>
            <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--status-escalated)', marginTop: 2 }}>
              {loadingStats ? '...' : stats.escalated_incidents}
            </div>
          </div>
        </div>
      </section>

      {/* ── 2. THE PARADIGM SHIFT COMPARISON ───────────────────────────── */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        <div style={{ textAlign: 'center', maxWidth: 700, margin: '0 auto' }}>
          <h2 style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-primary)' }}>
            The Structural Failure in Municipal Governance
          </h2>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 6 }}>
            Treating every citizen complaint as an isolated ticket creates waste, re-repair loops, and ignored hazards.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
          {/* Legacy System Card */}
          <div className="card" style={{
            padding: 24,
            borderLeft: '4px solid var(--status-critical)',
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{
                width: 28,
                height: 28,
                borderRadius: 6,
                background: 'rgba(239, 68, 68, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <span style={{ color: 'var(--status-critical)', fontWeight: 800 }}>✕</span>
              </div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
                Traditional Municipal Portals
              </h3>
            </div>
            <ul style={{ paddingLeft: 18, fontSize: 13, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 10 }}>
              <li><strong>Fragmented Complaints:</strong> A leaking water main, sub-base erosion, pothole, and flooding create 4 disconnected tickets across 3 departments.</li>
              <li><strong>Symptom Patching:</strong> Road department repaves asphalt over active leaks — new asphalt crumbles within days.</li>
              <li><strong>Volume ≠ Threat:</strong> 50 complaints about park bench paint take priority over 2 reports of a dangling live wire near an elementary school.</li>
              <li><strong>Contractor Fraud:</strong> Contractors mark tickets "Resolved" by uploading unrelated photos from distant locations without GPS validation.</li>
            </ul>
          </div>

          {/* OmniCivic AI Card */}
          <div className="card" style={{
            padding: 24,
            borderLeft: '4px solid var(--status-resolved)',
            background: 'linear-gradient(180deg, rgba(16, 185, 129, 0.04) 0%, transparent 100%)',
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{
                width: 28,
                height: 28,
                borderRadius: 6,
                background: 'rgba(16, 185, 129, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <ShieldCheck size={18} color="var(--status-resolved)" />
              </div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>
                OmniCivic AI Intelligence
              </h3>
            </div>
            <ul style={{ paddingLeft: 18, fontSize: 13, color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: 10 }}>
              <li><strong>Spatial-Temporal Correlation:</strong> Groups reports within 180m and 7 days using pure Haversine distance math.</li>
              <li><strong>Causal Root-Cause Discovery:</strong> Traverses civic dependency graphs to detect the true origin breakdown before dispatching crews.</li>
              <li><strong>Sequenced Department Work Orders:</strong> Enforces topological dependencies — Water Board isolates pipe before Roads Dept repaves.</li>
              <li><strong>Anti-Fraud Verification Gate:</strong> Dual-check GPS distance threshold (&lt;100m) and visual context matching before closing incidents.</li>
            </ul>
          </div>
        </div>
      </section>

      {/* ── 3. FOUR-STAGE ARCHITECTURAL WORKFLOW ───────────────────────── */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <div style={{ textAlign: 'center', maxWidth: 700, margin: '0 auto' }}>
          <h2 style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-primary)' }}>
            The Autonomous Multi-Agent Pipeline
          </h2>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 6 }}>
            Ten specialized agents work in concert, augmented by live external tools and multi-model LLM reasoning.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
          {/* Pillar 1 */}
          <div className="card" style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{
              width: 38,
              height: 38,
              borderRadius: 8,
              background: 'rgba(37, 99, 235, 0.12)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <Compass size={20} color="var(--accent-blue)" />
            </div>
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--accent-blue)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 01 · Ingestion & Grouping
            </span>
            <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
              Perception & Spatial Clustering
            </h4>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Multimodal models classify visual evidence, while the Clustering Agent aggregates co-located complaints within 180m radius and a 7-day rolling window.
            </p>
          </div>

          {/* Pillar 2 */}
          <div className="card" style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{
              width: 38,
              height: 38,
              borderRadius: 8,
              background: 'rgba(13, 148, 136, 0.12)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <CloudRain size={20} color="var(--accent-teal)" />
            </div>
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--accent-teal)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 02 · Grounded Enrichment
            </span>
            <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
              Keyless Analytical Tools
            </h4>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Executes live Open-Meteo 48h rain forecasts and OpenStreetMap Overpass queries to identify nearby schools, clinics, and transit hubs within 250m.
            </p>
          </div>

          {/* Pillar 3 */}
          <div className="card" style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{
              width: 38,
              height: 38,
              borderRadius: 8,
              background: 'rgba(245, 158, 11, 0.12)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <Workflow size={20} color="var(--status-high)" />
            </div>
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--status-high)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 03 · Causal Intelligence
            </span>
            <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
              Root Cause & Threat Scoring
            </h4>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Traverses the civic dependency graph to hypothesize the root cause chain. Computes a multi-factor threat score (0–100) grounded in physical risk.
            </p>
          </div>

          {/* Pillar 4 */}
          <div className="card" style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{
              width: 38,
              height: 38,
              borderRadius: 8,
              background: 'rgba(16, 185, 129, 0.12)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <FileCheck2 size={20} color="var(--status-resolved)" />
            </div>
            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--status-resolved)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 04 · Action & Verification
            </span>
            <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
              Response Plan & Anti-Fraud
            </h4>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              Generates sequenced department work orders requiring human authority sign-off. Enforces GPS proximity and photographic matching before ticket closure.
            </p>
          </div>
        </div>
      </section>

      {/* ── 4. REHEARSED LIVE DEMO SCENARIOS ───────────────────────────── */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-primary)' }}>
              Pre-Calibrated Live Scenarios
            </h2>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
              Test real cascading civic breakdown scenarios directly in the autonomous intelligence pipeline.
            </p>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-secondary"
            style={{ fontSize: 12, padding: '6px 14px' }}
          >
            Open Full Dashboard
            <ChevronRight size={14} />
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18 }}>
          {/* Scenario 1 */}
          <div className="card" style={{ padding: 20, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="badge badge-critical font-mono" style={{ fontSize: 10 }}>INC-2026-001</span>
                <span className="badge badge-critical" style={{ fontSize: 10 }}>CRITICAL (88/100)</span>
              </div>
              <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
                Water Main Burst Cascade
              </h4>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                Underground pipe burst near Chakala Junction erodes road sub-base, causing severe potholes that pool runoff into traffic-blocking waterlogging.
              </p>
              <div style={{ fontSize: 11, color: 'var(--accent-teal)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                <MapPin size={12} />
                Ward 7 · Andheri East (6 Co-located Reports)
              </div>
            </div>

            <button
              onClick={() => handleLaunchScenario('CIV-2026-1001')}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: 16, justifyContent: 'center', fontSize: 12, padding: '7px 12px' }}
            >
              <Play size={12} />
              Run Pipeline Analysis
            </button>
          </div>

          {/* Scenario 2 */}
          <div className="card" style={{ padding: 20, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="badge badge-high font-mono" style={{ fontSize: 10 }}>INC-2026-002</span>
                <span className="badge badge-high" style={{ fontSize: 10 }}>HIGH (76/100)</span>
              </div>
              <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
                Drainage-Waste Blockage Cycle
              </h4>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                Overflowing municipal garbage bins scatter debris into storm grates during downpours, causing backflow flooding in residential lanes.
              </p>
              <div style={{ fontSize: 11, color: 'var(--accent-teal)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                <MapPin size={12} />
                Ward 6 · Tilak Nagar, Kurla (4 Reports)
              </div>
            </div>

            <button
              onClick={() => handleLaunchScenario('CIV-2026-1011')}
              className="btn btn-secondary"
              style={{ width: '100%', marginTop: 16, justifyContent: 'center', fontSize: 12, padding: '7px 12px' }}
            >
              <Play size={12} />
              Run Pipeline Analysis
            </button>
          </div>

          {/* Scenario 3 */}
          <div className="card" style={{ padding: 20, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="badge badge-critical font-mono" style={{ fontSize: 10 }}>INC-2026-003</span>
                <span className="badge badge-critical" style={{ fontSize: 10 }}>CRITICAL (91/100)</span>
              </div>
              <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
                Live Electrical Wire Near School
              </h4>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                Exposed high-voltage wire hanging near a school entrance. Scored CRITICAL despite only 2 citizen reports, proving priority ≠ complaint count.
              </p>
              <div style={{ fontSize: 11, color: 'var(--accent-teal)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                <School size={12} />
                Ward 3 · St. Xavier's Gate (2 Reports)
              </div>
            </div>

            <button
              onClick={() => handleLaunchScenario('CIV-2026-1021')}
              className="btn btn-secondary"
              style={{ width: '100%', marginTop: 16, justifyContent: 'center', fontSize: 12, padding: '7px 12px' }}
            >
              <Play size={12} />
              Run Pipeline Analysis
            </button>
          </div>

          {/* Scenario 4 */}
          <div className="card" style={{ padding: 20, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="badge badge-medium font-mono" style={{ fontSize: 10 }}>INC-2026-004</span>
                <span className="badge badge-high" style={{ fontSize: 10 }}>REOPENED</span>
              </div>
              <h4 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
                Recurring Road Repair Failure
              </h4>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                Substandard contractor road patch fails within 3 weeks. Triggers automatic ticket reopening, contractor audit flags, and SLA deadline monitoring.
              </p>
              <div style={{ fontSize: 11, color: 'var(--accent-teal)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
                <RotateCcw size={12} />
                Ward 9 · Hill Road, Bandra West (3 Reports)
              </div>
            </div>

            <button
              onClick={() => handleLaunchScenario('CIV-2026-1031')}
              className="btn btn-secondary"
              style={{ width: '100%', marginTop: 16, justifyContent: 'center', fontSize: 12, padding: '7px 12px' }}
            >
              <Play size={12} />
              Run Pipeline Analysis
            </button>
          </div>
        </div>
      </section>

      {/* ── 5. MULTI-MODEL AI & SECURITY HARDENING ─────────────────────── */}
      <section className="card" style={{
        padding: 32,
        background: 'linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%)',
        border: '1px solid var(--border-secondary)',
        borderRadius: 16,
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 32, alignItems: 'center' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              fontSize: 11,
              fontWeight: 700,
              color: 'var(--accent-blue)',
              textTransform: 'uppercase',
            }}>
              <Lock size={14} />
              Enterprise Security & Model Neutrality
            </div>
            <h3 style={{ fontSize: 24, fontWeight: 800, color: 'var(--text-primary)' }}>
              Multi-Provider LLM Infrastructure
            </h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              No municipal vendor lock-in. Switch on-the-fly between ultra-fast cloud LPUs, frontier agentic reasoning loops, self-hosted local models, or 100% offline deterministic simulation.
            </p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 4 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 12, color: 'var(--text-secondary)' }}>
                <span style={{ color: 'var(--status-resolved)', fontWeight: 800 }}>✓</span>
                <span><strong>Fernet 256-bit Encryption at Rest:</strong> API credentials securely encrypted in <code>provider_configs.enc.json</code>.</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 12, color: 'var(--text-secondary)' }}>
                <span style={{ color: 'var(--status-resolved)', fontWeight: 800 }}>✓</span>
                <span><strong>Operator Token Authorization:</strong> Endpoints protected by auto-generated <code>X-Operator-Token</code> keys.</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 12, color: 'var(--text-secondary)' }}>
                <span style={{ color: 'var(--status-resolved)', fontWeight: 800 }}>✓</span>
                <span><strong>In-Flight Ping Diagnostics:</strong> Live 10s latency benchmarking with model discovery.</span>
              </div>
            </div>

            <div style={{ marginTop: 12 }}>
              <button
                onClick={() => navigate('/settings')}
                className="btn btn-primary"
                style={{ fontSize: 13, padding: '8px 18px', gap: 8 }}
              >
                <Cpu size={16} />
                Configure Providers in Settings
              </button>
            </div>
          </div>

          {/* Provider Grid Badges */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
            gap: 12,
            background: 'var(--bg-primary)',
            padding: 20,
            borderRadius: 12,
            border: '1px solid var(--border-primary)',
          }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, padding: 12, background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-primary)' }}>
              <img src={groqLogo} alt="Groq" style={{ width: 28, height: 28, objectFit: 'contain' }} />
              <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>Groq Cloud</span>
              <span style={{ fontSize: 9, color: 'var(--text-tertiary)' }}>Llama 3.3 / LPU</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, padding: 12, background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-primary)' }}>
              <img src={claudeLogo} alt="Claude" style={{ width: 28, height: 28, objectFit: 'contain' }} />
              <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>Claude Sonnet</span>
              <span style={{ fontSize: 9, color: 'var(--text-tertiary)' }}>Tool-Calling Loop</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, padding: 12, background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-primary)' }}>
              <img src={openaiLogo} alt="OpenAI" style={{ width: 28, height: 28, objectFit: 'contain' }} />
              <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>GPT-4o Mini</span>
              <span style={{ fontSize: 9, color: 'var(--text-tertiary)' }}>Structured Reasoning</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, padding: 12, background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-primary)' }}>
              <img src={geminiLogo} alt="Gemini" style={{ width: 28, height: 28, objectFit: 'contain' }} />
              <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>Gemini Flash</span>
              <span style={{ fontSize: 9, color: 'var(--text-tertiary)' }}>Multimodal Perception</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, padding: 12, background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-primary)' }}>
              <img src={ollamaLogo} alt="Ollama" style={{ width: 28, height: 28, objectFit: 'contain' }} />
              <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>Ollama Local</span>
              <span style={{ fontSize: 9, color: 'var(--text-tertiary)' }}>Offline Self-Hosted</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, padding: 12, background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-primary)' }}>
              <ShieldCheck size={28} color="var(--status-resolved)" />
              <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>Zero-Key Sim</span>
              <span style={{ fontSize: 9, color: 'var(--status-resolved)' }}>100% Offline Mode</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── 6. FOOTER CTA CALLOUT ──────────────────────────────────────── */}
      <section style={{
        textAlign: 'center',
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-primary)',
        borderRadius: 16,
        padding: '48px 24px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 16,
      }}>
        <div style={{
          width: 44,
          height: 44,
          borderRadius: 12,
          background: 'linear-gradient(135deg, #2563EB 0%, #0D9488 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(37, 99, 235, 0.4)',
        }}>
          <Activity size={24} color="#ffffff" />
        </div>
        
        <h2 style={{ fontSize: 26, fontWeight: 800, color: 'var(--text-primary)' }}>
          Ready to experience the future of urban infrastructure?
        </h2>
        <p style={{ fontSize: 14, color: 'var(--text-secondary)', maxWidth: 600 }}>
          Launch the Operations Dashboard to trigger autonomous pipeline runs on live citizen complaint clusters, inspect causal trees, and verify field repairs.
        </p>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 8 }}>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-primary"
            style={{ padding: '12px 28px', fontSize: 14, fontWeight: 700, borderRadius: 8 }}
          >
            Go to Operations Dashboard
          </button>
          <button
            onClick={() => navigate('/report')}
            className="btn btn-secondary"
            style={{ padding: '12px 24px', fontSize: 14, fontWeight: 600, borderRadius: 8 }}
          >
            Submit a Test Complaint
          </button>
        </div>
      </section>

    </div>
  );
}
