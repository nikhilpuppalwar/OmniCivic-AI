import { useState } from 'react';
import { 
  ChevronDown, 
  ChevronRight, 
  Terminal, 
  Wrench, 
  Cpu, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  BrainCircuit, 
  FileText 
} from 'lucide-react';
import type { AgentTraceStep } from '../lib/api';

interface ToolTraceCardProps {
  trace?: AgentTraceStep[];
  reasoningMode?: string;
}

export default function ToolTraceCard({ trace = [], reasoningMode = 'agentic_multi_turn' }: ToolTraceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedStepIndex, setExpandedStepIndex] = useState<number | null>(null);

  if (!trace || trace.length === 0) {
    return null;
  }

  const totalLatency = trace.reduce((acc, step) => acc + (step.latency_ms || 0), 0);
  const toolCallCount = trace.filter(s => s.type === 'tool_call' || s.tool || s.tool_name).length;
  const hasErrors = trace.some(s => !!s.error);

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'model_call':
        return { label: 'Model Turn', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.12)', icon: BrainCircuit };
      case 'tool_call':
        return { label: 'Tool Call', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.12)', icon: Wrench };
      case 'tool_result':
        return { label: 'Tool Result', color: '#10b981', bg: 'rgba(16, 185, 129, 0.12)', icon: CheckCircle2 };
      case 'final':
        return { label: 'Final Synthesis', color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.12)', icon: FileText };
      case 'deterministic':
        return { label: 'Deterministic Rule', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.12)', icon: Cpu };
      case 'single_turn':
        return { label: 'Single Turn', color: '#6366f1', bg: 'rgba(99, 102, 241, 0.12)', icon: Terminal };
      default:
        return { label: type, color: '#9ca3af', bg: 'rgba(156, 163, 175, 0.12)', icon: Terminal };
    }
  };

  const getModeLabel = (mode: string) => {
    switch (mode) {
      case 'agentic_multi_turn':
        return { label: 'Autonomous Agentic', color: '#10b981', bg: 'rgba(16, 185, 129, 0.15)' };
      case 'single_turn_enriched':
        return { label: 'Enriched Prompt', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.15)' };
      case 'deterministic_fallback':
      default:
        return { label: 'Deterministic Fallback', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)' };
    }
  };

  const modeBadge = getModeLabel(reasoningMode);

  return (
    <div className="card" style={{
      marginTop: 14,
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border-primary)',
      borderRadius: 8,
      overflow: 'hidden'
    }}>
      {/* Header bar - click to expand/collapse */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          width: '100%',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 16px',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          color: 'inherit',
          textAlign: 'left'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {isExpanded ? <ChevronDown size={16} color="var(--accent-blue)" /> : <ChevronRight size={16} color="var(--text-tertiary)" />}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Terminal size={14} color="var(--accent-blue)" />
            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
              Agent Execution Trace
            </span>
            <span style={{
              fontSize: 10,
              padding: '2px 8px',
              borderRadius: 12,
              fontWeight: 600,
              background: modeBadge.bg,
              color: modeBadge.color
            }}>
              {modeBadge.label}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>
            {trace.length} {trace.length === 1 ? 'step' : 'steps'} ({toolCallCount} tools)
          </span>
          {totalLatency > 0 && (
            <span style={{
              fontSize: 10,
              fontFamily: 'monospace',
              color: 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              gap: 4
            }}>
              <Clock size={11} /> {totalLatency}ms
            </span>
          )}
          {hasErrors && (
            <span style={{
              fontSize: 10,
              color: 'var(--status-critical)',
              background: 'rgba(239, 68, 68, 0.12)',
              padding: '2px 6px',
              borderRadius: 4,
              display: 'flex',
              alignItems: 'center',
              gap: 4
            }}>
              <AlertCircle size={11} /> Failure Handled
            </span>
          )}
          <span style={{ fontSize: 11, color: 'var(--accent-blue)', fontWeight: 500 }}>
            {isExpanded ? 'Collapse' : 'Inspect Timeline'}
          </span>
        </div>
      </button>

      {/* Expanded timeline body */}
      {isExpanded && (
        <div style={{
          padding: '12px 16px 16px',
          borderTop: '1px solid var(--border-primary)',
          background: 'var(--bg-primary)'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {trace.map((step, idx) => {
              const typeBadge = getTypeBadge(step.type);
              const Icon = typeBadge.icon;
              const toolName = step.tool || step.tool_name;
              const stepArgs = step.args || step.arguments;
              const stepResult = step.result || step.result_summary;
              const isDetailsOpen = expandedStepIndex === idx;

              return (
                <div
                  key={idx}
                  style={{
                    background: 'var(--bg-secondary)',
                    border: `1px solid ${step.error ? 'rgba(239, 68, 68, 0.4)' : 'var(--border-secondary)'}`,
                    borderRadius: 6,
                    padding: '8px 12px',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                      <span style={{
                        fontSize: 10,
                        fontWeight: 700,
                        color: 'var(--text-tertiary)',
                        fontFamily: 'monospace'
                      }}>
                        #{step.step || idx + 1}
                      </span>

                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 4,
                        fontSize: 10,
                        fontWeight: 600,
                        padding: '2px 6px',
                        borderRadius: 4,
                        background: typeBadge.bg,
                        color: typeBadge.color
                      }}>
                        <Icon size={11} />
                        {typeBadge.label}
                      </span>

                      {toolName && (
                        <span style={{
                          fontSize: 11,
                          fontWeight: 600,
                          fontFamily: 'monospace',
                          color: 'var(--text-primary)',
                          background: 'rgba(255, 255, 255, 0.05)',
                          padding: '1px 6px',
                          borderRadius: 4
                        }}>
                          {toolName}
                        </span>
                      )}

                      {step.summary && (
                        <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                          {step.summary}
                        </span>
                      )}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      {step.latency_ms !== undefined && step.latency_ms > 0 && (
                        <span style={{ fontSize: 10, fontFamily: 'monospace', color: 'var(--text-tertiary)' }}>
                          {step.latency_ms}ms
                        </span>
                      )}

                      {(stepArgs || stepResult || step.error) && (
                        <button
                          onClick={() => setExpandedStepIndex(isDetailsOpen ? null : idx)}
                          style={{
                            background: 'none',
                            border: 'none',
                            color: 'var(--accent-blue)',
                            fontSize: 10,
                            cursor: 'pointer',
                            padding: '2px 4px'
                          }}
                        >
                          {isDetailsOpen ? 'Hide Payload' : 'View Payload'}
                        </button>
                      )}
                    </div>
                  </div>

                  {step.error && (
                    <div style={{
                      marginTop: 6,
                      fontSize: 11,
                      color: '#ef4444',
                      background: 'rgba(239, 68, 68, 0.08)',
                      padding: '4px 8px',
                      borderRadius: 4,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6
                    }}>
                      <AlertCircle size={12} />
                      <span>{step.error}</span>
                    </div>
                  )}

                  {/* Expandable JSON / Payload Details */}
                  {isDetailsOpen && (
                    <div style={{
                      marginTop: 8,
                      padding: '8px 10px',
                      background: 'var(--bg-tertiary)',
                      borderRadius: 4,
                      fontSize: 11,
                      fontFamily: 'monospace',
                      color: 'var(--text-secondary)',
                      overflowX: 'auto'
                    }}>
                      {stepArgs && Object.keys(stepArgs).length > 0 && (
                        <div style={{ marginBottom: 6 }}>
                          <span style={{ color: 'var(--accent-blue)', fontWeight: 600 }}>Arguments: </span>
                          <pre style={{ margin: '4px 0 0', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                            {JSON.stringify(stepArgs, null, 2)}
                          </pre>
                        </div>
                      )}
                      {stepResult && (
                        <div>
                          <span style={{ color: '#10b981', fontWeight: 600 }}>Result: </span>
                          <pre style={{ margin: '4px 0 0', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                            {typeof stepResult === 'string' ? stepResult : JSON.stringify(stepResult, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
