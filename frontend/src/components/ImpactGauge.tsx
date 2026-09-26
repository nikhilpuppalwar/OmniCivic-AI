import type { ImpactBreakdown } from '../lib/api';

interface ImpactGaugeProps {
  score: number;
  priority: string;
  breakdown: ImpactBreakdown;
  explanation: string;
}

export default function ImpactGauge({ score, priority, breakdown, explanation }: ImpactGaugeProps) {
  const getPriorityClass = (pri: string) => {
    switch (pri) {
      case 'CRITICAL': return 'badge-critical';
      case 'HIGH': return 'badge-high';
      case 'MEDIUM': return 'badge-medium';
      default: return 'badge-low';
    }
  };

  // SVG Gauge calculations
  const radius = 50;
  const stroke = 8;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const factors = [
    { label: 'Severity (30%)', val: breakdown.severity_score },
    { label: 'Infrastructure Proximity (20%)', val: breakdown.infrastructure_proximity },
    { label: 'People Affected (15%)', val: breakdown.people_affected },
    { label: 'Duration (10%)', val: breakdown.duration },
    { label: 'Repeat Reports (10%)', val: breakdown.repeat_reports },
    { label: 'Secondary Risk (15%)', val: breakdown.secondary_risk },
  ];

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 16 }}>
        Civic Impact Assessment
      </h3>

      <div style={{ display: 'flex', gap: 20, alignItems: 'center', marginBottom: 16 }}>
        {/* SVG Radial Gauge */}
        <div style={{ position: 'relative', width: 100, height: 100, flexShrink: 0 }}>
          <svg height={100} width={100}>
            <circle
              stroke="var(--border-primary)"
              fill="transparent"
              strokeWidth={stroke}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            <circle
              stroke={priority === 'CRITICAL' ? 'var(--status-critical)' : priority === 'HIGH' ? 'var(--status-high)' : 'var(--accent-blue)'}
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={circumference + ' ' + circumference}
              style={{ strokeDashoffset }}
              strokeLinecap="round"
              r={normalizedRadius}
              cx={radius}
              cy={radius}
              className="gauge-ring"
              transform="rotate(-90 50 50)"
            />
          </svg>
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
          }}>
            <span className="font-mono" style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)' }}>
              {Math.round(score)}
            </span>
            <span style={{ fontSize: 8, color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              Impact Score
            </span>
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
            <span className={`badge ${getPriorityClass(priority)}`}>
              {priority}
            </span>
          </div>
          <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
            {explanation || 'No impact narrative generated.'}
          </p>
        </div>
      </div>

      <div style={{
        marginTop: 'auto',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 12,
        paddingTop: 12,
        borderTop: '1px solid var(--border-primary)',
      }}>
        {factors.map((f, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10 }}>
              <span style={{ color: 'var(--text-secondary)' }}>{f.label}</span>
              <span className="font-mono" style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
                {Math.round(f.val)}
              </span>
            </div>
            <div style={{ height: 4, background: 'var(--border-primary)', borderRadius: 2, overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${f.val}%`,
                background: f.val > 75 ? 'var(--status-critical)' : f.val > 50 ? 'var(--status-high)' : 'var(--accent-blue)',
                borderRadius: 2,
              }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
