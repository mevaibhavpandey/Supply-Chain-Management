import Link from 'next/link';

const DIMENSIONS = [
  { name: 'Specification Completeness', weight: '20%', desc: 'README, docstrings, entry points', icon: '📋' },
  { name: 'Input / Output Clarity', weight: '15%', desc: 'Type hints, Pydantic schemas, I/O docs', icon: '🔌' },
  { name: 'Reliability & Error Handling', weight: '20%', desc: 'try/except, retry logic, timeouts, deps', icon: '🛡️' },
  { name: 'Security Hygiene', weight: '20%', desc: 'Secrets, eval/exec, subprocess safety', icon: '🔒' },
  { name: 'Observability / Logging', weight: '10%', desc: 'Logging framework, structured logs', icon: '📊' },
  { name: 'SCM Readiness', weight: '15%', desc: 'Domain vocabulary, config, tests, Docker', icon: '⛓️' },
];

const STEPS = [
  { label: 'Submit', desc: 'GitHub URL, ZIP, or individual files' },
  { label: 'Ingest & Analyze', desc: '18 deterministic rules, 6 dimensions' },
  { label: 'Score', desc: 'Weighted trust score 0-100' },
  { label: 'Review', desc: 'Interactive dashboard with recommendations' },
];

export default function HomePage() {
  return (
    <div>
      {/* ── Hero ─────────────────────────────────────────────────── */}
      <section
        className="page-header"
        style={{
          paddingTop: 80,
          paddingBottom: 80,
          textAlign: 'center',
          background:
            'radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.12) 0%, transparent 70%)',
        }}
      >
        <div className="container">
          <div style={{ marginBottom: 24 }}>
            <span className="feature-badge">🔬 Deterministic • Zero AI in Scoring</span>
          </div>

          <h1
            className="page-title"
            style={{ fontSize: 'clamp(32px, 5vw, 56px)', maxWidth: 800, margin: '0 auto 20px' }}
          >
            Validate Your{' '}
            <span className="gradient-text">SCM AI Agent</span>
            <br />
            Before It Touches Production
          </h1>

          <p
            className="page-subtitle"
            style={{ maxWidth: 560, margin: '0 auto 40px', fontSize: 18, lineHeight: 1.7 }}
          >
            A deterministic trust-scoring platform that audits your Supply Chain AI agent
            across 6 critical dimensions using 18 rule-based checks. Same agent, same rules,
            same score — every time.
          </p>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/submit" className="btn btn-primary btn-lg">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
              Start Validation
            </Link>
            <Link href="/history" className="btn btn-secondary btn-lg">
              View History
            </Link>
          </div>

          <div
            style={{
              display: 'flex',
              gap: 32,
              justifyContent: 'center',
              marginTop: 48,
              flexWrap: 'wrap',
            }}
          >
            {[
              { value: '18', label: 'Rule Checks' },
              { value: '6', label: 'Trust Dimensions' },
              { value: '100%', label: 'Deterministic' },
              { value: '<30s', label: 'Validation Time' },
            ].map((s) => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <div
                  style={{
                    fontSize: 28,
                    fontWeight: 800,
                    background: 'var(--gradient-brand)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  {s.value}
                </div>
                <div style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 4 }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ─────────────────────────────────────────── */}
      <section style={{ padding: '64px 0' }}>
        <div className="container">
          <h2
            style={{
              fontSize: 24,
              fontWeight: 700,
              marginBottom: 40,
              textAlign: 'center',
              color: 'var(--color-text-secondary)',
            }}
          >
            How It Works
          </h2>
          <div className="grid-4">
            {STEPS.map((step, i) => (
              <div
                key={step.label}
                className="card animate-fade-in"
                style={{
                  animationDelay: `${i * 0.1}s`,
                  background: 'var(--gradient-card)',
                  textAlign: 'center',
                }}
              >
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    background: 'var(--color-indigo-dim)',
                    border: '1px solid rgba(99,102,241,0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 16px',
                    fontWeight: 800,
                    color: 'var(--color-indigo-light)',
                    fontSize: 14,
                  }}
                >
                  {i + 1}
                </div>
                <div style={{ fontWeight: 700, marginBottom: 8 }}>{step.label}</div>
                <div style={{ fontSize: 13, color: 'var(--color-text-muted)', lineHeight: 1.5 }}>
                  {step.desc}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Dimensions ───────────────────────────────────────────── */}
      <section style={{ padding: '0 0 80px' }}>
        <div className="container">
          <h2
            style={{
              fontSize: 24,
              fontWeight: 700,
              marginBottom: 8,
              textAlign: 'center',
            }}
          >
            6 Trust Dimensions
          </h2>
          <p
            style={{
              textAlign: 'center',
              color: 'var(--color-text-secondary)',
              marginBottom: 40,
              fontSize: 14,
            }}
          >
            Each dimension is independently scored and weighted into the overall trust score
          </p>
          <div className="grid-3">
            {DIMENSIONS.map((dim, i) => (
              <div
                key={dim.name}
                className="card animate-fade-in"
                style={{ animationDelay: `${i * 0.08}s` }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                  <span style={{ fontSize: 24 }}>{dim.icon}</span>
                  <span
                    className="badge badge-indigo"
                    style={{ marginLeft: 'auto' }}
                  >
                    {dim.weight}
                  </span>
                </div>
                <div style={{ fontWeight: 700, marginBottom: 6, fontSize: 15 }}>{dim.name}</div>
                <div style={{ fontSize: 13, color: 'var(--color-text-muted)', lineHeight: 1.5 }}>
                  {dim.desc}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────── */}
      <section style={{ padding: '0 0 80px' }}>
        <div className="container">
          <div
            className="card"
            style={{
              textAlign: 'center',
              padding: '60px 40px',
              background: 'linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.05) 100%)',
              border: '1px solid rgba(99,102,241,0.2)',
            }}
          >
            <h2 style={{ fontSize: 28, fontWeight: 800, marginBottom: 12 }}>
              Ready to Validate Your Agent?
            </h2>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: 32, maxWidth: 480, margin: '0 auto 32px' }}>
              Submit a GitHub URL, upload a ZIP, or drag and drop your agent files.
              Get a full validation report in under 30 seconds.
            </p>
            <Link href="/submit" className="btn btn-primary btn-lg">
              Start Free Validation →
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
