import { useState } from 'react';
import type { ResponseStep } from '../lib/api';
import { Play, ShieldCheck } from 'lucide-react';

interface ResponsePlanProps {
  incidentId: string;
  steps: ResponseStep[];
  rationale: string;
  approved: boolean;
  onApprove: () => Promise<void>;
}

export default function ResponsePlan({ incidentId, steps, rationale, approved, onApprove }: ResponsePlanProps) {
  const [loading, setLoading] = useState(false);

  const handleApprove = async () => {
    setLoading(true);
    try {
      await onApprove();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
          Multi-Department Response Plan for {incidentId}
        </h3>
        {approved ? (
          <span className="badge badge-resolved" style={{ gap: 4 }}>
            <ShieldCheck size={12} />
            Execution Approved
          </span>
        ) : (
          <span className="badge badge-high" style={{ gap: 4 }}>
            Awaiting Approval
          </span>
        )}
      </div>

      <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
        {rationale || 'Orchestrating response steps based on causal dependencies...'}
      </p>

      {/* Steps visualization */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {steps.map((step) => (
          <div key={step.step_number} style={{
            display: 'flex',
            gap: 12,
            padding: 12,
            background: 'var(--bg-primary)',
            border: '1px solid var(--border-primary)',
            borderRadius: 6,
          }}>
            <div style={{
              width: 20,
              height: 20,
              borderRadius: '50%',
              background: approved ? 'var(--status-resolved-bg)' : 'var(--bg-tertiary)',
              border: `1px solid ${approved ? 'var(--status-resolved)' : 'var(--border-secondary)'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 10,
              fontWeight: 700,
              color: approved ? 'var(--status-resolved)' : 'var(--text-secondary)',
              flexShrink: 0,
            }}>
              {step.step_number}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 4 }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>
                  {step.department_name}
                </span>
                <span className="font-mono" style={{ fontSize: 10, color: 'var(--text-tertiary)' }}>
                  SLA: {step.estimated_hours}h
                </span>
              </div>

              <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                {step.action}
              </span>

              {step.depends_on && step.depends_on.length > 0 && (
                <div style={{ display: 'flex', gap: 4, alignItems: 'center', marginTop: 4 }}>
                  <span style={{ fontSize: 9, color: 'var(--status-high)' }}>
                    Requires:
                  </span>
                  {step.depends_on.map((dep, i) => (
                    <span key={i} className="font-mono" style={{
                      fontSize: 8,
                      padding: '1px 4px',
                      background: 'rgba(245, 158, 11, 0.08)',
                      border: '1px solid rgba(245, 158, 11, 0.2)',
                      borderRadius: 3,
                      color: 'var(--status-high)',
                    }}>
                      {dep}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Human-in-the-loop Gate Button */}
      {!approved && (
        <button
          className="btn btn-primary"
          onClick={handleApprove}
          disabled={loading || steps.length === 0}
          style={{ width: '100%', justifyContent: 'center', marginTop: 6 }}
        >
          {loading ? (
            <span className="spinner" />
          ) : (
            <>
              <Play size={14} />
              Approve Multi-Department Plan
            </>
          )}
        </button>
      )}
    </div>
  );
}
