import { useState } from 'react';
import { ShieldAlert, CheckCircle2, AlertTriangle, ChevronDown, ChevronRight, Sparkles } from 'lucide-react';
import type { ReflectionMetadata } from '../lib/api';

interface RootCauseCardProps {
  hypothesis: string;
  confidence: number;
  evidence: string[];
  chain: string[];
  disclaimer: string;
  toolsUsed?: string[];
  reasoningMode?: string;
  reasoningNotes?: string;
  reflection?: ReflectionMetadata;
}

export default function RootCauseCard({
  hypothesis,
  confidence,
  evidence,
  chain,
  disclaimer,
  toolsUsed = [],
  reasoningMode = 'agentic_multi_turn',
  reasoningNotes = '',
  reflection,
}: RootCauseCardProps) {
  const [showReflectionDetails, setShowReflectionDetails] = useState(false);

  const getToolBadge = (tool: string) => {
    switch (tool) {
      case 'get_weather_forecast':
        return { label: '🌧️ Weather forecast', bg: 'rgba(59, 130, 246, 0.15)', text: '#60a5fa' };
      case 'find_nearby_sensitive_sites':
        return { label: '🏫 Nearby sensitive sites', bg: 'rgba(16, 185, 129, 0.15)', text: '#34d399' };
      case 'query_dependency_graph':
        return { label: '📊 Dependency graph', bg: 'rgba(139, 92, 246, 0.15)', text: '#a78bfa' };
      case 'get_historical_incidents':
        return { label: '📜 Historical incidents', bg: 'rgba(245, 158, 11, 0.15)', text: '#fbbf24' };
      case 'compute_distance':
        return { label: '📏 Distance verification', bg: 'rgba(236, 72, 153, 0.15)', text: '#f472b6' };
      default:
        return { label: `🛠️ ${tool.replace(/_/g, ' ')}`, bg: 'rgba(107, 114, 128, 0.15)', text: '#9ca3af' };
    }
  };

  const getModeBadge = (mode?: string) => {
    switch (mode) {
      case 'agentic_multi_turn':
        return { label: 'Autonomous Agentic', bg: 'rgba(16, 185, 129, 0.18)', text: '#10b981', border: 'rgba(16, 185, 129, 0.4)' };
      case 'single_turn_enriched':
        return { label: 'Enriched Prompt', bg: 'rgba(59, 130, 246, 0.18)', text: '#60a5fa', border: 'rgba(59, 130, 246, 0.4)' };
      case 'deterministic_fallback':
      default:
        return { label: 'Deterministic Fallback', bg: 'rgba(245, 158, 11, 0.18)', text: '#fbbf24', border: 'rgba(245, 158, 11, 0.4)' };
    }
  };

  const modeBadge = getModeBadge(reasoningMode);

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header with Title, Mode Badge, and Confidence */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
            Root Cause Investigation
          </h3>
          <span style={{
            fontSize: 9,
            padding: '2px 7px',
            borderRadius: 4,
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.03em',
            background: modeBadge.bg,
            color: modeBadge.text,
            border: `1px solid ${modeBadge.border}`,
          }}>
            {modeBadge.label}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 10, color: 'var(--text-secondary)' }}>Confidence:</span>
          <span className="font-mono" style={{
            fontSize: 11,
            fontWeight: 600,
            color: confidence > 0.75 ? 'var(--status-resolved)' : confidence > 0.5 ? 'var(--status-high)' : 'var(--status-critical)'
          }}>
            {Math.round(confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Dynamic Tool Badges (only tools actually invoked) */}
      {toolsUsed.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 10 }}>
          {Array.from(new Set(toolsUsed)).map((tool, idx) => {
            const badge = getToolBadge(tool);
            return (
              <span key={idx} style={{
                fontSize: 10,
                padding: '2px 8px',
                borderRadius: 12,
                background: badge.bg,
                color: badge.text,
                fontWeight: 500,
              }}>
                {badge.label}
              </span>
            );
          })}
        </div>
      )}

      {/* Causal Chain Visualization */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 6,
        padding: '10px 12px',
        background: 'var(--bg-primary)',
        borderRadius: 6,
        border: '1px solid var(--border-primary)',
        marginBottom: 14,
      }}>
        {chain.map((item, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              padding: '4px 10px',
              background: i === 0 ? 'rgba(239, 68, 68, 0.12)' : 'var(--bg-tertiary)',
              border: `1px solid ${i === 0 ? 'rgba(239, 68, 68, 0.4)' : 'var(--border-secondary)'}`,
              borderRadius: 6,
              boxShadow: i === 0 ? '0 0 10px rgba(239, 68, 68, 0.2)' : 'none',
            }}>
              <span style={{ fontSize: 8, color: i === 0 ? '#EF4444' : 'var(--text-tertiary)', fontWeight: 700, textTransform: 'uppercase' }}>
                {i === 0 ? 'ROOT CAUSE' : i === chain.length - 1 ? 'RESULTING IMPACT' : 'PROPAGATION'}
              </span>
              <span className="font-mono" style={{
                fontSize: 11,
                color: i === 0 ? '#EF4444' : 'var(--text-primary)',
                fontWeight: 700,
              }}>
                {item.replace(/_/g, ' ')}
              </span>
            </div>
            {i < chain.length - 1 && (
              <span style={{ fontSize: 14, color: 'var(--accent-blue)', fontWeight: 700 }}>➔</span>
            )}
          </div>
        ))}
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div>
          <span style={{ fontSize: 11, color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: 4 }}>
            HYPOTHESIS
          </span>
          <p style={{ fontSize: 12, color: 'var(--text-primary)', lineHeight: 1.4 }}>
            {hypothesis || 'Analyzing causal relationships...'}
          </p>
        </div>

        {evidence && evidence.length > 0 && (
          <div>
            <span style={{ fontSize: 11, color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: 4 }}>
              EVIDENCE & PROPAGATION MECHANISM
            </span>
            <ul style={{
              margin: 0,
              paddingLeft: 16,
              fontSize: 11,
              color: 'var(--text-secondary)',
              display: 'flex',
              flexDirection: 'column',
              gap: 4,
            }}>
              {evidence.map((item, i) => (
                <li key={i} style={{ lineHeight: 1.4 }}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Critic / Reflection Section */}
      {reflection && (
        <div style={{
          marginTop: 12,
          padding: '8px 12px',
          background: 'var(--bg-primary)',
          borderRadius: 6,
          border: '1px solid var(--border-primary)',
        }}>
          <div
            onClick={() => setShowReflectionDetails(!showReflectionDetails)}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              cursor: 'pointer',
              userSelect: 'none',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Sparkles size={13} color="var(--accent-blue)" />
              <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-primary)' }}>
                Critic Self-Reflection
              </span>
              <span style={{
                fontSize: 9,
                padding: '1px 6px',
                borderRadius: 4,
                fontWeight: 700,
                textTransform: 'uppercase',
                background: reflection.verdict === 'approved' ? 'rgba(16, 185, 129, 0.15)' :
                            reflection.verdict === 'revised' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                color: reflection.verdict === 'approved' ? '#10b981' :
                       reflection.verdict === 'revised' ? '#60a5fa' : '#ef4444',
                border: `1px solid ${reflection.verdict === 'approved' ? 'rgba(16, 185, 129, 0.3)' :
                                      reflection.verdict === 'revised' ? 'rgba(59, 130, 246, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
              }}>
                {reflection.verdict}
              </span>
              <span style={{ fontSize: 10, color: 'var(--text-tertiary)' }}>
                ({reflection.iterations || 1} pass{(reflection.iterations || 1) > 1 ? 'es' : ''})
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ fontSize: 10, color: 'var(--text-tertiary)' }}>
                {reflection.checks ? `${reflection.checks.filter(c => c.passed).length}/${reflection.checks.length} checks passed` : ''}
              </span>
              {showReflectionDetails ? <ChevronDown size={14} color="var(--text-tertiary)" /> : <ChevronRight size={14} color="var(--text-tertiary)" />}
            </div>
          </div>

          {/* Revisions alert if any were applied */}
          {reflection.revisions_applied && reflection.revisions_applied.length > 0 && (
            <div style={{
              marginTop: 6,
              fontSize: 10,
              color: '#60a5fa',
              background: 'rgba(59, 130, 246, 0.08)',
              padding: '4px 8px',
              borderRadius: 4,
              border: '1px dashed rgba(59, 130, 246, 0.3)'
            }}>
              <strong>Revisions applied:</strong> {reflection.revisions_applied.join('; ')}
            </div>
          )}

          {/* Collapsible Checks detail */}
          {showReflectionDetails && reflection.checks && reflection.checks.length > 0 && (
            <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
              {reflection.checks.map((check, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 6,
                  fontSize: 10,
                  color: check.passed ? 'var(--text-secondary)' : '#ef4444',
                }}>
                  {check.passed ? (
                    <CheckCircle2 size={12} color="#10b981" style={{ flexShrink: 0, marginTop: 1 }} />
                  ) : (
                    <AlertTriangle size={12} color="#ef4444" style={{ flexShrink: 0, marginTop: 1 }} />
                  )}
                  <span>
                    <strong>{check.name}:</strong> {check.detail}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {reasoningNotes && (
        <div style={{
          marginTop: 12,
          padding: '6px 10px',
          background: 'var(--bg-primary)',
          borderRadius: 6,
          border: '1px solid var(--border-primary)',
          fontSize: 11,
          color: 'var(--text-secondary)',
          fontStyle: 'italic',
        }}>
          💡 <strong>Notes:</strong> {reasoningNotes}
        </div>
      )}

      {disclaimer && (
        <div style={{
          marginTop: 16,
          padding: '8px 12px',
          background: 'rgba(239, 68, 68, 0.06)',
          border: '1px dashed rgba(239, 68, 68, 0.25)',
          borderRadius: 6,
          display: 'flex',
          gap: 8,
          alignItems: 'flex-start',
        }}>
          <ShieldAlert size={14} color="var(--status-critical)" style={{ marginTop: 2, flexShrink: 0 }} />
          <span style={{ fontSize: 10, color: 'var(--text-secondary)', lineHeight: 1.3 }}>
            <strong>DISCLAIMER:</strong> {disclaimer}
          </span>
        </div>
      )}
    </div>
  );
}
