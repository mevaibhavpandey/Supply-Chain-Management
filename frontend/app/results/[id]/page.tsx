'use client';

import { use, useEffect, useState } from 'react';
import Link from 'next/link';
import { getValidationResults, ValidationResult, Finding, Recommendation } from '@/lib/api';

// ── Trust Score Ring ──────────────────────────────────────────────────────────
function ScoreRing({ score, verdict, color }: { score: number; verdict: string; color: string }) {
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="score-ring-container" style={{ width: 200, height: 200 }}>
      <svg className="score-ring-svg" width="200" height="200" viewBox="0 0 200 200">
        {/* Background track */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke="rgba(99,102,241,0.1)"
          strokeWidth="14"
        />
        {/* Score arc */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)', filter: `drop-shadow(0 0 8px ${color}60)` }}
        />
      </svg>
      <div className="score-ring-label">
        <div style={{ fontSize: 40, fontWeight: 900, lineHeight: 1, color }}>{score}</div>
        <div style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 4 }}>/100</div>
        <div style={{ fontSize: 11, fontWeight: 700, marginTop: 6, color }}>{verdict}</div>
      </div>
    </div>
  );
}

// ── Dimension Bar Row ─────────────────────────────────────────────────────────
function DimensionRow({
  name, score, weight, remarks,
}: {
  name: string; score: number; weight: number; remarks: string;
}) {
  const pct = score;
  const barColor = pct >= 80 ? 'var(--color-success)' : pct >= 50 ? 'var(--color-warning)' : 'var(--color-danger)';

  return (
    <div style={{ padding: '14px 0', borderBottom: '1px solid var(--color-border)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 14, fontWeight: 600 }}>{name}</span>
          <span className="badge badge-indigo" style={{ fontSize: 10 }}>{(weight * 100).toFixed(0)}%</span>
        </div>
        <span style={{ fontSize: 16, fontWeight: 800, color: barColor }}>{score.toFixed(1)}</span>
      </div>
      <div className="progress-bar" style={{ marginBottom: 6 }}>
        <div
          style={{
            height: '100%',
            borderRadius: '9999px',
            background: barColor,
            width: `${pct}%`,
            transition: 'width 1s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: `0 0 8px ${barColor}60`,
          }}
        />
      </div>
      <div style={{ fontSize: 12, color: 'var(--color-text-muted)', lineHeight: 1.5 }}>{remarks}</div>
    </div>
  );
}

// ── Finding Card ──────────────────────────────────────────────────────────────
function FindingCard({
  finding,
  recommendation,
}: {
  finding: Finding;
  recommendation?: Recommendation;
}) {
  const [open, setOpen] = useState(false);
  const [recOpen, setRecOpen] = useState(false);

  const sev = finding.severity.toLowerCase();
  const badgeClass = `badge badge-${sev}`;

  return (
    <div className={`finding-card severity-${sev}`} style={{ marginBottom: 8 }}>
      {/* Header */}
      <div
        className="collapsible-header"
        onClick={() => setOpen(!open)}
        id={`finding-${finding.id}`}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1, minWidth: 0 }}>
          <span className={badgeClass}>{finding.severity}</span>
          <span style={{ fontWeight: 600, fontSize: 14, color: 'var(--color-text-primary)' }}>
            {finding.title}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
          <span style={{ fontSize: 12, color: 'var(--color-danger)' }}>−{finding.score_impact}pts</span>
          <span style={{ fontSize: 11, color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
            {finding.rule_id}
          </span>
          <svg
            width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="var(--color-text-muted)" strokeWidth="2"
            style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s', flexShrink: 0 }}
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </div>

      {/* Body */}
      {open && (
        <div style={{ padding: '0 20px 20px' }} className="animate-fade-in">
          <div className="divider" style={{ margin: '0 0 16px' }} />

          <div style={{ marginBottom: 14 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              What was detected
            </div>
            <div style={{ fontSize: 14, color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
              {finding.description}
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Why it matters
            </div>
            <div style={{ fontSize: 14, color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
              {finding.why_it_matters}
            </div>
          </div>

          {/* Recommendation */}
          {recommendation && (
            <div
              style={{
                background: 'var(--color-bg-primary)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                overflow: 'hidden',
              }}
            >
              <div
                className="collapsible-header"
                onClick={() => setRecOpen(!recOpen)}
                style={{ padding: '12px 16px' }}
              >
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-indigo-light)' }}>
                  💡 {recommendation.title}
                </span>
                <svg
                  width="14" height="14" viewBox="0 0 24 24" fill="none"
                  stroke="var(--color-text-muted)" strokeWidth="2"
                  style={{ transform: recOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </div>
              {recOpen && (
                <div style={{ padding: '0 16px 16px' }} className="animate-fade-in">
                  <div style={{ fontSize: 13, color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: 12 }}>
                    {recommendation.recommendation}
                  </div>
                  {recommendation.implementation_guidance && (
                    <pre className="code-block" style={{ fontSize: 11, lineHeight: 1.7 }}>
                      {recommendation.implementation_guidance}
                    </pre>
                  )}
                  <div style={{ marginTop: 12, fontSize: 12, color: 'var(--color-success)' }}>
                    ✓ {recommendation.expected_impact}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Main Results Page ─────────────────────────────────────────────────────────
export default function ResultsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'findings' | 'dimensions' | 'insights'>('findings');
  const [severityFilter, setSeverityFilter] = useState<string>('All');

  useEffect(() => {
    getValidationResults(id)
      .then(setResult)
      .catch((e) => setError(e.message || 'Failed to load results.'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div style={{ maxWidth: 900, margin: '80px auto', padding: '0 24px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton" style={{ height: 80, borderRadius: 12 }} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div style={{ maxWidth: 600, margin: '80px auto', padding: '0 24px', textAlign: 'center' }}>
        <div className="alert alert-error">{error || 'Results not found.'}</div>
        <Link href="/history" className="btn btn-secondary" style={{ marginTop: 16 }}>
          ← Back to History
        </Link>
      </div>
    );
  }

  const { summary, score_breakdown, findings, recommendations, ai_insights } = result;
  const recMap = Object.fromEntries(recommendations.map((r) => [r.finding_id, r]));
  const filteredFindings =
    severityFilter === 'All'
      ? findings
      : findings.filter((f) => f.severity === severityFilter);

  const severityCounts = findings.reduce<Record<string, number>>(
    (acc, f) => { acc[f.severity] = (acc[f.severity] || 0) + 1; return acc; },
    {}
  );

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '40px 24px 80px' }}>
      {/* ── Top Bar ── */}
      <div
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}
        className="animate-fade-in"
      >
        <div>
          <div style={{ fontSize: 12, color: 'var(--color-text-muted)', marginBottom: 4 }}>
            Validation Results
          </div>
          <h1 style={{ fontSize: 24, fontWeight: 800 }}>{summary.agent_name}</h1>
          {summary.scm_use_case && (
            <div style={{ marginTop: 6 }}>
              <span className="badge badge-indigo">{summary.scm_use_case}</span>
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link href="/submit" className="btn btn-secondary">
            + New Validation
          </Link>
          <Link href="/history" className="btn btn-ghost">
            History
          </Link>
        </div>
      </div>

      {/* ── Summary Cards ── */}
      <div className="grid-4 animate-fade-in animate-delay-100" style={{ marginBottom: 32 }}>
        {/* Score Ring */}
        <div
          className="card"
          style={{
            gridColumn: 'span 1',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 24,
            background: 'var(--gradient-card)',
          }}
        >
          <ScoreRing
            score={summary.overall_trust_score}
            verdict={summary.verdict}
            color={summary.verdict_color}
          />
        </div>

        {/* Stats */}
        <div className="stat-card">
          <div className="stat-label">Total Findings</div>
          <div className="stat-value" style={{ color: 'var(--color-text-primary)' }}>
            {summary.total_findings}
          </div>
          <div className="stat-desc">issues detected</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Critical / High</div>
          <div
            className="stat-value"
            style={{ color: summary.critical_findings > 0 ? 'var(--color-danger)' : 'var(--color-warning)' }}
          >
            {summary.critical_findings + summary.high_findings}
          </div>
          <div className="stat-desc">{summary.critical_findings} critical, {summary.high_findings} high</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Submission</div>
          <div className="stat-value" style={{ fontSize: 16, color: 'var(--color-text-secondary)', fontWeight: 700 }}>
            {summary.submission_type === 'repo_url' ? 'GitHub URL' : summary.submission_type.toUpperCase()}
          </div>
          <div className="stat-desc">
            {new Date(summary.timestamp).toLocaleString()}
          </div>
        </div>
      </div>

      {/* ── Tabs ── */}
      <div className="tab-group animate-fade-in animate-delay-200" style={{ marginBottom: 24 }}>
        <button
          className={`tab ${activeTab === 'findings' ? 'active' : ''}`}
          onClick={() => setActiveTab('findings')}
          id="tab-findings"
        >
          Findings ({findings.length})
        </button>
        <button
          className={`tab ${activeTab === 'dimensions' ? 'active' : ''}`}
          onClick={() => setActiveTab('dimensions')}
          id="tab-dimensions"
        >
          Score Breakdown
        </button>
        {ai_insights.length > 0 && (
          <button
            className={`tab ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
            id="tab-insights"
          >
            AI Insights ({ai_insights.length})
          </button>
        )}
      </div>

      {/* ── Findings Tab ── */}
      {activeTab === 'findings' && (
        <div className="animate-fade-in">
          {/* Severity Filter */}
          <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
            {['All', 'Critical', 'High', 'Medium', 'Low'].map((s) => (
              <button
                key={s}
                onClick={() => setSeverityFilter(s)}
                className={`btn btn-sm ${severityFilter === s ? 'btn-primary' : 'btn-secondary'}`}
                id={`filter-${s.toLowerCase()}`}
              >
                {s}
                {s !== 'All' && severityCounts[s] ? ` (${severityCounts[s]})` : ''}
              </button>
            ))}
          </div>

          {filteredFindings.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">✓</div>
              <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
                No {severityFilter === 'All' ? '' : severityFilter} findings!
              </div>
              <div style={{ color: 'var(--color-text-muted)' }}>
                This agent passed all checks in this category.
              </div>
            </div>
          ) : (
            filteredFindings.map((finding, i) => (
              <div key={finding.id} className="animate-fade-in" style={{ animationDelay: `${i * 0.05}s` }}>
                <FindingCard
                  finding={finding}
                  recommendation={recMap[finding.id]}
                />
              </div>
            ))
          )}
        </div>
      )}

      {/* ── Dimensions Tab ── */}
      {activeTab === 'dimensions' && (
        <div className="card animate-fade-in">
          <h3 style={{ fontWeight: 700, marginBottom: 24, fontSize: 16 }}>
            Trust Score Breakdown by Dimension
          </h3>
          {score_breakdown.map((dim) => (
            <DimensionRow
              key={dim.dimension}
              name={dim.display_name}
              score={dim.score}
              weight={dim.weight}
              remarks={dim.remarks}
            />
          ))}
        </div>
      )}

      {/* ── AI Insights Tab ── */}
      {activeTab === 'insights' && (
        <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div
            className="alert alert-info"
            style={{ marginBottom: 8 }}
          >
            <span>🤖</span>
            <div>
              <div style={{ fontWeight: 600, marginBottom: 2 }}>AI-Generated Insights</div>
              <div style={{ fontSize: 13 }}>
                These insights are supplemental commentary from GPT and do NOT affect the trust score.
              </div>
            </div>
          </div>

          {ai_insights.map((insight) => (
            <div key={insight.id} className="card">
              <div
                style={{
                  fontSize: 11,
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  color: 'var(--color-indigo-light)',
                  marginBottom: 10,
                }}
              >
                {insight.insight_type.replace(/_/g, ' ')}
              </div>
              <div style={{ fontSize: 14, lineHeight: 1.7, color: 'var(--color-text-secondary)' }}>
                {insight.content}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Run ID Footer ── */}
      <div style={{ marginTop: 40, fontSize: 12, color: 'var(--color-text-muted)', textAlign: 'center' }}>
        Run ID: <code style={{ fontFamily: 'monospace', color: 'var(--color-text-secondary)' }}>{id}</code>
        {' · '}
        {new Date(summary.timestamp).toLocaleString()}
      </div>
    </div>
  );
}
