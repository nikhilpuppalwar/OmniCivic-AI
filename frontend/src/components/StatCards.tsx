import type { DashboardStats } from '../lib/api';
import { AlertCircle, CheckCircle2, ShieldAlert, FileWarning, RefreshCw, Layers } from 'lucide-react';

interface StatCardsProps {
  stats: DashboardStats;
}

export default function StatCards({ stats }: StatCardsProps) {
  const cards = [
    {
      label: 'Total Reports',
      value: stats.total_reports,
      sublabel: 'Ingested complaints',
      icon: <Layers size={18} color="#3B82F6" />,
      accentColor: '#3B82F6',
      bgColor: 'rgba(59, 130, 246, 0.06)',
    },
    {
      label: 'Active Incidents',
      value: stats.active_incidents,
      sublabel: 'Clustered incident groups',
      icon: <FileWarning size={18} color="#60A5FA" />,
      accentColor: '#60A5FA',
      bgColor: 'rgba(96, 165, 250, 0.06)',
    },
    {
      label: 'Critical Priority',
      value: stats.critical_incidents,
      sublabel: 'Requires immediate dispatch',
      icon: <ShieldAlert size={18} color="#EF4444" />,
      accentColor: '#EF4444',
      badge: stats.critical_incidents > 0 ? 'Urgent' : null,
      badgeColor: 'badge-critical',
      bgColor: 'rgba(239, 68, 68, 0.08)',
    },
    {
      label: 'Resolved',
      value: stats.resolved_incidents,
      sublabel: 'Verified & closed',
      icon: <CheckCircle2 size={18} color="#10B981" />,
      accentColor: '#10B981',
      bgColor: 'rgba(16, 185, 129, 0.06)',
    },
    {
      label: 'Reopened Cases',
      value: stats.reopened_incidents,
      sublabel: 'Follow-up investigation',
      icon: <RefreshCw size={18} color="#F59E0B" />,
      accentColor: '#F59E0B',
      bgColor: 'rgba(245, 158, 11, 0.06)',
    },
    {
      label: 'Escalated SLAs',
      value: stats.escalated_incidents,
      sublabel: 'Deadline exceeded',
      icon: <AlertCircle size={18} color="#A855F7" />,
      accentColor: '#A855F7',
      badge: stats.escalated_incidents > 0 ? 'Breach' : null,
      badgeColor: 'badge-escalated',
      bgColor: 'rgba(168, 85, 247, 0.08)',
    },
  ];


  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
      gap: 12,
      marginBottom: 20,
    }}>
      {cards.map((card, i) => (
        <div
          key={i}
          className="card"
          style={{
            padding: '14px 16px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            minHeight: 96,
            background: card.bgColor,

            borderLeft: `3px solid ${card.accentColor}`,
            position: 'relative',
            overflow: 'hidden',
            transition: 'all 0.2s ease',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 11, color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              {card.label}
            </span>
            <div style={{
              padding: 6,
              borderRadius: 6,
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.06)',
            }}>
              {card.icon}
            </div>
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginTop: 8 }}>
              <span className="font-mono" style={{ fontSize: 26, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                {card.value}
              </span>
              {card.badge && (
                <span className={`badge ${card.badgeColor}`} style={{ fontSize: 9, padding: '2px 6px' }}>
                  {card.badge}
                </span>
              )}
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-tertiary)', marginTop: 2 }}>
              {card.sublabel}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

