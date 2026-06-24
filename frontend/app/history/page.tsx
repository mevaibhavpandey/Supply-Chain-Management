'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getHistory, deleteValidation, HistoryItem } from '@/lib/api';

const STATUS_COLORS: Record<string, string> = {
  complete: 'var(--color-success)',
  running: 'var(--color-indigo)',
  pending: 'var(--color-warning)',
  failed: 'var(--color-danger)',
};

const VERDICT_COLORS: Record<string, string> = {
  'Production Ready': 'var(--color-success)',
  'Demo Ready': 'var(--color-indigo-light)',
  'Conditionally Ready': 'var(--color-warning)',
  'High Risk': 'var(--color-orange)',
  'Critical Risk': 'var(--color-danger)',
};

function ScorePill({ score, verdict }: { score?: number; verdict?: string }) {
  if (score == null) return <span style={{ color: 'var(--color-text-muted)', fontSize: 13 }}>—</span>;
  const color = verdict ? VERDICT_COLORS[verdict] || 'var(--color-text-secondary)' : 'var(--color-text-secondary)';
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
      <span style={{ fontSize: 20, fontWeight: 800, color, lineHeight: 1 }}>{score}</span>
      {verdict && (
        <span style={{ fontSize: 10, color, fontWeight: 600, marginTop: 2, whiteSpace: 'nowrap' }}>
          {verdict}
        </span>
      )}
    </div>
  );
}

export default function HistoryPage() {
  const [runs, setRuns] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);

  const perPage = 20;

  const load = async (p = 1) => {
    setLoading(true);
    try {
      const data = await getHistory(p, perPage);
      setRuns(data.runs);
      setTotal(data.total);
      setPage(p);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); }, []);

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this validation run?')) return;
    setDeleting(id);
    try {
      await deleteValidation(id);
      setRuns((prev) => prev.filter((r) => r.id !== id));
      setTotal((t) => t - 1);
    } catch {
      alert('Failed to delete. Please try again.');
    } finally {
      setDeleting(null);
    }
  };

  const totalPages = Math.ceil(total / perPage);

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '40px 24px 80px' }}>
      {/* Header */}
      <div
        className="animate-fade-in"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 32,
        }}
      >
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 4 }}>Validation History</h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 14 }}>
            {total} total run{total !== 1 ? 's' : ''}
          </p>
        </div>
        <Link href="/submit" className="btn btn-primary">
          + New Validation
        </Link>
      </div>

      {/* Table */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="skeleton" style={{ height: 72, borderRadius: 12 }} />
          ))}
        </div>
      ) : runs.length === 0 ? (
        <div className="card empty-state">
          <div className="empty-state-icon">📋</div>
          <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>No Validations Yet</div>
          <p style={{ color: 'var(--color-text-muted)', marginBottom: 24, maxWidth: 400 }}>
            Submit your first SCM AI agent for validation to see the results here.
          </p>
          <Link href="/submit" className="btn btn-primary">
            Start Validation
          </Link>
        </div>
      ) : (
        <div>
          {/* Column Headers */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '2fr 120px 100px 80px 80px',
              gap: 16,
              padding: '8px 16px',
              fontSize: 11,
              fontWeight: 700,
              color: 'var(--color-text-muted)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: 8,
            }}
          >
            <span>Agent</span>
            <span>Status</span>
            <span>Type</span>
            <span>Findings</span>
            <span style={{ textAlign: 'right' }}>Score</span>
          </div>

          {/* Rows */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {runs.map((run, i) => (
              <div
                key={run.id}
                className="card animate-fade-in"
                style={{
                  padding: '16px',
                  animationDelay: `${i * 0.04}s`,
                  display: 'grid',
                  gridTemplateColumns: '2fr 120px 100px 80px 80px',
                  gap: 16,
                  alignItems: 'center',
                  cursor: run.status === 'complete' ? 'pointer' : 'default',
                }}
                onClick={() => {
                  if (run.status === 'complete') {
                    window.location.href = `/results/${run.id}`;
                  } else if (run.status === 'running' || run.status === 'pending') {
                    window.location.href = `/validating/${run.id}`;
                  }
                }}
              >
                {/* Agent Info */}
                <div>
                  <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>
                    {run.agent_name}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
                    {new Date(run.created_at).toLocaleString()}
                    {run.scm_use_case && (
                      <span style={{ marginLeft: 8 }}>
                        · <span style={{ color: 'var(--color-indigo-light)' }}>{run.scm_use_case}</span>
                      </span>
                    )}
                  </div>
                </div>

                {/* Status */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: STATUS_COLORS[run.status] || 'var(--color-text-muted)',
                      animation: run.status === 'running' ? 'pulse-glow 1.5s ease infinite' : 'none',
                    }}
                  />
                  <span
                    style={{
                      fontSize: 13,
                      fontWeight: 600,
                      color: STATUS_COLORS[run.status] || 'var(--color-text-muted)',
                      textTransform: 'capitalize',
                    }}
                  >
                    {run.status}
                  </span>
                </div>

                {/* Type */}
                <span
                  style={{
                    fontSize: 12,
                    color: 'var(--color-text-muted)',
                    background: 'var(--color-bg-secondary)',
                    padding: '3px 8px',
                    borderRadius: 4,
                    border: '1px solid var(--color-border)',
                  }}
                >
                  {run.submission_type === 'repo_url' ? 'URL' : run.submission_type.toUpperCase()}
                </span>

                {/* Findings */}
                <span style={{ fontSize: 13, color: 'var(--color-text-secondary)', fontWeight: 600 }}>
                  {run.total_findings > 0 ? (
                    <span style={{ color: run.total_findings > 5 ? 'var(--color-danger)' : 'var(--color-warning)' }}>
                      {run.total_findings}
                    </span>
                  ) : run.status === 'complete' ? (
                    <span style={{ color: 'var(--color-success)' }}>0</span>
                  ) : (
                    '—'
                  )}
                </span>

                {/* Score + Delete */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 8 }}>
                  <ScorePill score={run.overall_score} verdict={run.verdict} />
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={(e) => { e.stopPropagation(); handleDelete(run.id); }}
                    disabled={deleting === run.id}
                    style={{ color: 'var(--color-text-muted)', padding: '4px 8px' }}
                    title="Delete run"
                    id={`delete-${run.id}`}
                  >
                    {deleting === run.id ? (
                      <div className="animate-spin" style={{ width: 12, height: 12, border: '1.5px solid currentColor', borderTop: '1.5px solid transparent', borderRadius: '50%' }} />
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6l-1 14H6L5 6" />
                        <path d="M10 11v6M14 11v6" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 24 }}>
              <button
                className="btn btn-secondary btn-sm"
                disabled={page <= 1}
                onClick={() => load(page - 1)}
              >
                ← Prev
              </button>
              <span
                style={{
                  padding: '7px 14px',
                  fontSize: 13,
                  color: 'var(--color-text-secondary)',
                }}
              >
                Page {page} of {totalPages}
              </span>
              <button
                className="btn btn-secondary btn-sm"
                disabled={page >= totalPages}
                onClick={() => load(page + 1)}
              >
                Next →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
