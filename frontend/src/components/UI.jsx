import React from 'react';

export function getFitTier(score) {
  const num = Number(score) || 0;
  if (num >= 75) return { tier: 'high', label: 'High Fit', color: '#10B981', cls: 'fit-high' };
  if (num >= 50) return { tier: 'mid', label: 'Partial Fit', color: '#F59E0B', cls: 'fit-mid' };
  return { tier: 'low', label: 'Low Fit', color: '#F43F5E', cls: 'fit-low' };
}

export function ScoreRing({ score }) {
  const { cls } = getFitTier(score);
  return (
    <span className={`fit-badge ${cls} tabular-score`} style={{ fontSize: '0.85rem', padding: '0.25rem 0.6rem' }}>
      {Math.round(score)}%
    </span>
  );
}

export function FitBar({ score }) {
  const { cls } = getFitTier(score);
  const rounded = Math.round(Number(score) || 0);
  return (
    <div className="fit-bar-container">
      <div className={`score-display ${cls}`}>
        <span className="tabular-score">{rounded}</span>
        <span className="score-unit">%</span>
      </div>
      <div className="fit-bar-track">
        <div
          className={`fit-bar-fill ${cls}`}
          style={{ width: `${Math.max(3, Math.min(100, rounded))}%` }}
        />
      </div>
    </div>
  );
}

export function CandidateRow({
  rank,
  title,
  subtitle,
  company,
  score,
  matchedSkills = [],
  missingSkills = [],
  extraActions,
  onClick,
}) {
  const { cls, label } = getFitTier(score);
  return (
    <div className="candidate-row" onClick={onClick}>
      <div className="candidate-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {rank !== undefined && <RankBadge rank={rank} />}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <h4 className="candidate-title">{title}</h4>
              {company && (
                <span className="company-badge">
                  🏢 {company}
                </span>
              )}
            </div>
            {subtitle && <p className="candidate-subtitle">{subtitle}</p>}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <span className={`fit-badge ${cls}`}>{label}</span>
          {extraActions}
        </div>
      </div>

      {/* Signature element: horizontal fit bar next to tabular score */}
      <FitBar score={score} />

      {/* Matched and missing skill chips below it */}
      <div className="skills-chips-row">
        {matchedSkills.length > 0 && (
          <div className="chips-group">
            <span className="chips-label">Matched:</span>
            {matchedSkills.map((s, idx) => (
              <span key={idx} className="chip chip-matched">✓ {s}</span>
            ))}
          </div>
        )}
        {missingSkills.length > 0 && (
          <div className="chips-group">
            <span className="chips-label">Missing:</span>
            {missingSkills.map((s, idx) => (
              <span key={idx} className="chip chip-missing">✕ {s}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function ProgressBar({ value, color }) {
  return (
    <div className="fit-bar-track" style={{ height: 6 }}>
      <div
        className="fit-bar-fill"
        style={{
          width: `${Math.min(100, Math.max(0, value))}%`,
          background: color || 'var(--gradient-brand)',
        }}
      />
    </div>
  );
}

export function SkillTags({ skills = [], variant = 'neutral' }) {
  if (!skills?.length) return <span className="text-muted" style={{ fontSize: '0.8rem' }}>—</span>;
  const chipCls = variant === 'matched' ? 'chip-matched' : variant === 'missing' ? 'chip-missing' : 'chip-neutral';
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
      {skills.map((s, i) => (
        <span key={i} className={`chip ${chipCls}`}>{s}</span>
      ))}
    </div>
  );
}

export function StatCard({ icon, label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div>
        <div className="stat-label">{label}</div>
        <div className="stat-value">{value}</div>
      </div>
    </div>
  );
}

export function Loader({ text = 'Loading...' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '3.5rem', gap: '1rem' }}>
      <div className="spinner" />
      <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.925rem', fontWeight: 500 }}>{text}</p>
    </div>
  );
}

export function EmptyState({ icon = '📄', title, desc, action }) {
  return (
    <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem' }}>
      <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>{icon}</div>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.4rem', color: '#FFFFFF' }}>{title}</h3>
      {desc && <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.925rem', maxWidth: 440, margin: '0 auto' }}>{desc}</p>}
      {action && <div style={{ marginTop: '1.5rem' }}>{action}</div>}
    </div>
  );
}

export function RankBadge({ rank }) {
  const isTop = rank === 1;
  return (
    <span
      className="fit-badge tabular-score"
      style={{
        fontWeight: 800,
        minWidth: 32,
        justifyContent: 'center',
        background: isTop ? 'rgba(245, 158, 11, 0.15)' : 'rgba(255, 255, 255, 0.05)',
        borderColor: isTop ? 'rgba(245, 158, 11, 0.4)' : 'var(--border-color)',
        color: isTop ? '#FBBF24' : '#CBD5E1',
      }}
    >
      #{rank}
    </span>
  );
}
