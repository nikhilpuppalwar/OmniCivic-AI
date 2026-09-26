import { useState } from 'react';
import { api } from '../lib/api';
import { RotateCcw, CalendarClock, ShieldAlert } from 'lucide-react';

interface DemoControlsProps {
  currentIncidentId?: string;
  onReset: () => Promise<void>;
  onTimeAdvanced: () => Promise<void>;
}

export default function DemoControls({ currentIncidentId, onReset, onTimeAdvanced }: DemoControlsProps) {
  const [resetting, setResetting] = useState(false);
  const [advancing, setAdvancing] = useState(false);

  const handleReset = async () => {
    setResetting(true);
    try {
      await api.resetDemo();
      await onReset();
    } catch (e) {
      console.error(e);
      alert('Failed to reset demo');
    } finally {
      setResetting(false);
    }
  };

  const handleAdvanceTime = async () => {
    if (!currentIncidentId) return;
    setAdvancing(true);
    try {
      await api.advanceDemoTime(currentIncidentId, 72); // Advance 3 days
      await onTimeAdvanced();
    } catch (e) {
      console.error(e);
      alert('Failed to advance time');
    } finally {
      setAdvancing(false);
    }
  };

  return (
    <div className="card card-elevated" style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 12,
      border: '1px solid var(--border-secondary)',
    }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
        <ShieldAlert size={14} color="var(--accent-blue)" />
        Demo Controls
      </h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        {/* Reset button */}
        <button
          className="btn btn-secondary"
          onClick={handleReset}
          disabled={resetting}
          style={{ justifyContent: 'center' }}
        >
          {resetting ? (
            <span className="spinner" />
          ) : (
            <>
              <RotateCcw size={13} />
              Reset Demo
            </>
          )}
        </button>

        {/* Time advance button */}
        <button
          className="btn btn-secondary animate-pulse"
          onClick={handleAdvanceTime}
          disabled={advancing || !currentIncidentId}
          style={{
            justifyContent: 'center',
            borderColor: currentIncidentId ? 'var(--status-high)' : 'var(--border-primary)',
            color: currentIncidentId ? 'var(--status-high)' : 'var(--text-tertiary)',
            background: currentIncidentId ? 'rgba(245, 158, 11, 0.04)' : 'transparent',
          }}
        >
          {advancing ? (
            <span className="spinner" />
          ) : (
            <>
              <CalendarClock size={13} />
              Advance Time (+3 Days)
            </>
          )}
        </button>
      </div>

      <span style={{ fontSize: 9, color: 'var(--text-tertiary)', textAlign: 'center' }}>
        * Advance Time triggers SLA breach and escalates priority incidents.
      </span>
    </div>
  );
}
