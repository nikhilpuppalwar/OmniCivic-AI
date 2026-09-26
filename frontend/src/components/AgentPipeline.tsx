import { CheckCircle2, Circle, Loader2, AlertTriangle, ChevronRight } from 'lucide-react';

interface PipelineStage {
  id: string;
  name: string;
  agent: string;
  status: 'pending' | 'running' | 'complete' | 'error' | 'waiting';
  result?: string;
  confidence?: number;
}

interface AgentPipelineProps {
  stages: PipelineStage[];
}

const stageIcons = {
  pending: <Circle size={16} style={{ color: 'var(--text-tertiary)' }} />,
  running: <Loader2 size={16} style={{ color: 'var(--accent-blue)', animation: 'spin 1s linear infinite' }} />,
  complete: <CheckCircle2 size={16} style={{ color: '#10B981' }} />,
  error: <AlertTriangle size={16} style={{ color: 'var(--status-critical)' }} />,
  waiting: <Circle size={16} style={{ color: 'var(--status-high)' }} />,
};


export default function AgentPipeline({ stages }: AgentPipelineProps) {
  const completedCount = stages.filter(s => s.status === 'complete').length;
  const progressPct = Math.round((completedCount / stages.length) * 100);

  return (
    <div className="card" style={{ padding: '16px 20px', background: 'var(--bg-secondary)', border: '1px solid var(--border-primary)' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 14,
        paddingBottom: 10,
        borderBottom: '1px solid var(--border-primary)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: completedCount === stages.length ? '#10B981' : '#3B82F6' }}></span>
            Multi-Agent Reasoning Pipeline
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>
            Autonomous perception to response orchestration
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* Progress bar */}
          <div style={{ width: 80, height: 4, borderRadius: 2, background: 'var(--bg-tertiary)', overflow: 'hidden' }}>
            <div style={{ width: `${progressPct}%`, height: '100%', background: 'linear-gradient(90deg, #2563EB, #10B981)', transition: 'width 0.4s ease' }} />
          </div>
          <span style={{
            fontSize: 10,
            color: completedCount === stages.length ? '#10B981' : 'var(--accent-blue)',
            background: completedCount === stages.length ? 'rgba(16, 185, 129, 0.12)' : 'rgba(37, 99, 235, 0.12)',
            border: `1px solid ${completedCount === stages.length ? 'rgba(16, 185, 129, 0.3)' : 'rgba(37, 99, 235, 0.3)'}`,
            padding: '2px 8px',
            borderRadius: 12,
            fontWeight: 700,
          }}>
            {completedCount}/{stages.length} STAGES
          </span>
        </div>
      </div>

      {/* Pipeline visualization */}
      <div style={{
        display: 'flex',
        alignItems: 'stretch',
        gap: 0,
        overflowX: 'auto',
        padding: '4px 0 8px',
      }}>
        {stages.map((stage, i) => (
          <div key={stage.id} style={{ display: 'flex', alignItems: 'center' }}>
            {/* Stage card */}
            <div
              className="animate-fade-in"
              style={{
                display: 'flex',
                flexDirection: 'column',
                padding: '10px 14px',
                borderRadius: 8,
                border: `1px solid ${stage.status === 'running' ? 'var(--accent-blue)' : stage.status === 'complete' ? 'rgba(16, 185, 129, 0.4)' : 'var(--border-primary)'}`,
                boxShadow: stage.status === 'running' ? '0 0 14px rgba(37, 99, 235, 0.35)' : stage.status === 'complete' ? '0 2px 8px rgba(0,0,0,0.2)' : 'none',
                background: stage.status === 'running'
                  ? 'rgba(37, 99, 235, 0.12)'
                  : stage.status === 'complete'
                  ? 'rgba(16, 185, 129, 0.08)'
                  : 'var(--bg-tertiary)',

                minWidth: 135,
                position: 'relative',
                animationDelay: `${i * 80}ms`,
                opacity: 0,
                transition: 'all 0.3s ease',
              }}
            >
              {/* Step number badge */}
              <span className="font-mono" style={{ position: 'absolute', top: 6, right: 8, fontSize: 9, fontWeight: 700, color: 'var(--text-tertiary)', opacity: 0.6 }}>
                0{i + 1}
              </span>

              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                {stageIcons[stage.status]}
                <span style={{
                  fontSize: 11,
                  fontWeight: 700,
                  color: stage.status === 'pending' ? 'var(--text-tertiary)' : 'var(--text-primary)',
                }}>
                  {stage.name}
                </span>
              </div>

              <span className="font-mono" style={{
                fontSize: 9,
                color: 'var(--text-tertiary)',
                marginBottom: stage.result ? 4 : 0,
              }}>
                {stage.agent}
              </span>

              {stage.result && (
                <span style={{
                  fontSize: 10,
                  color: 'var(--text-secondary)',
                  marginTop: 4,
                  lineHeight: 1.3,
                  fontWeight: 500,
                }}>
                  {stage.result}
                </span>
              )}

              {stage.confidence !== undefined && stage.status === 'complete' && (
                <div style={{ marginTop: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
                  <div style={{
                    width: 44,
                    height: 3,
                    borderRadius: 2,
                    background: 'var(--bg-primary)',
                    overflow: 'hidden',
                  }}>
                    <div style={{
                      width: `${stage.confidence * 100}%`,
                      height: '100%',
                      background: stage.confidence > 0.7 ? '#10B981' : stage.confidence > 0.4 ? '#F59E0B' : '#EF4444',
                      borderRadius: 2,
                      transition: 'width 0.5s ease-out',
                    }} />
                  </div>
                  <span className="font-mono" style={{ fontSize: 9, color: 'var(--text-tertiary)' }}>
                    {(stage.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              )}

              {stage.status === 'waiting' && (
                <span style={{
                  fontSize: 10,
                  color: 'var(--status-high)',
                  marginTop: 4,
                  fontWeight: 600,
                }}>
                  Awaiting approval
                </span>
              )}
            </div>

            {/* Connector Chevron */}
            {i < stages.length - 1 && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                padding: '0 4px',
              }}>
                <ChevronRight
                  size={16}
                  style={{
                    color: stage.status === 'complete'
                      ? '#10B981'
                      : stage.status === 'running'
                      ? '#3B82F6'
                      : 'var(--border-secondary)',
                    transition: 'color 0.3s',
                    flexShrink: 0,
                  }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}


// Helper to build stages from pipeline result
export function buildPipelineStages(
  pipelineResult?: Record<string, { status: string; result: Record<string, unknown> }>,
  isRunning: boolean = false,
): PipelineStage[] {
  const stageConfig = [
    { id: 'perception', name: 'Perception', agent: 'perception_agent' },
    { id: 'clustering', name: 'Clustering', agent: 'clustering_agent' },
    { id: 'incident_detection', name: 'Detection', agent: 'incident_agent' },
    { id: 'root_cause', name: 'Root Cause', agent: 'root_cause_agent' },
    { id: 'impact', name: 'Impact', agent: 'impact_agent' },
    { id: 'response', name: 'Response', agent: 'response_agent' },
    { id: 'filing', name: 'Filing', agent: 'filing_agent' },
  ];

  if (!pipelineResult) {
    return stageConfig.map((s, i) => ({
      ...s,
      status: isRunning && i === 0 ? 'running' as const : 'pending' as const,
    }));
  }

  let foundIncomplete = false;
  return stageConfig.map((s) => {
    const stage = pipelineResult[s.id];
    if (!stage) {
      if (!foundIncomplete) {
        foundIncomplete = true;
        return { ...s, status: isRunning ? 'running' as const : 'pending' as const };
      }
      return { ...s, status: 'pending' as const };
    }

    const result = stage.result || {};
    let resultStr = '';
    let confidence: number | undefined;

    switch (s.id) {
      case 'perception':
        resultStr = `${result.issue_type || ''} · ${result.severity || ''}`;
        confidence = result.confidence as number;
        break;
      case 'clustering':
        resultStr = `${result.cluster_size || 0} related reports`;
        break;
      case 'incident_detection':
        resultStr = (result.classification as string || '').replace(/_/g, ' ');
        confidence = result.confidence as number;
        break;
      case 'root_cause': {
        const chain = result.chain as string[] || [];
        resultStr = chain.join(' → ');
        confidence = result.confidence as number;
        break;
      }
      case 'impact':
        resultStr = `${result.score || 0}/100 · ${result.priority || ''}`;
        break;
      case 'response': {
        const steps = result.steps as Array<Record<string, unknown>> || [];
        const approved = result.approved as boolean;
        resultStr = `${steps.length} steps`;
        if (approved) resultStr += ' · Approved';
        break;
      }
      case 'filing':
        resultStr = 'Complaint filed';
        break;
    }

    return {
      ...s,
      status: stage.status === 'complete' ? 'complete' as const : 'pending' as const,
      result: resultStr,
      confidence,
    };
  });
}
