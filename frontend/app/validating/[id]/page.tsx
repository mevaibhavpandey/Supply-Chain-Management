'use client';

import { use, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getValidationStatus, ValidationStatus } from '@/lib/api';

const STEPS = [
  { key: 'ingest', label: 'Ingesting agent source', desc: 'Cloning repository or reading uploaded files' },
  { key: 'static', label: 'Running static analysis', desc: 'Detecting language, framework, and file structure' },
  { key: 'rules', label: 'Executing validation rules', desc: '18 deterministic checks across 6 dimensions' },
  { key: 'scoring', label: 'Calculating trust score', desc: 'Weighted scoring of all dimensions' },
  { key: 'evidence', label: 'Gathering evidence', desc: 'Mapping findings to source code locations' },
  { key: 'recommendations', label: 'Building recommendations', desc: 'Generating actionable fix guidance' },
  { key: 'persist', label: 'Saving results', desc: 'Persisting validation report to database' },
];

function getStepIndex(progress: number): number {
  if (progress < 20) return 0;
  if (progress < 40) return 1;
  if (progress < 60) return 2;
  if (progress < 70) return 3;
  if (progress < 80) return 4;
  if (progress < 92) return 5;
  return 6;
}

export default function ValidatingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [status, setStatus] = useState<ValidationStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let timer: NodeJS.Timeout;

    const poll = async () => {
      try {
        const s = await getValidationStatus(id);
        if (cancelled) return;
        setStatus(s);

        if (s.status === 'complete') {
          // Brief pause then redirect
          timer = setTimeout(() => {
            router.push(`/results/${id}`);
          }, 800);
          return;
        }

        if (s.status === 'failed') {
          setError(s.error_message || 'Validation failed. Please try again.');
          return;
        }

        // Poll again in 1.5s
        timer = setTimeout(poll, 1500);
      } catch (err: any) {
        if (cancelled) return;
        setError(err?.message || 'Failed to fetch validation status.');
      }
    };

    poll();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [id, router]);

  const progress = status?.progress ?? 0;
  const currentStepIdx = getStepIndex(progress);
  const isComplete = status?.status === 'complete';
  const isFailed = status?.status === 'failed';

  return (
    <div style={{ maxWidth: 640, margin: '0 auto', padding: '80px 24px' }}>
      <div className="animate-fade-in" style={{ textAlign: 'center', marginBottom: 48 }}>
        {/* Animated Logo */}
        <div
          style={{
            width: 72,
            height: 72,
            margin: '0 auto 24px',
            borderRadius: '50%',
            background: 'var(--color-indigo-dim)',
            border: '2px solid var(--color-indigo)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            animation: isComplete ? 'none' : 'pulse-glow 2s ease-in-out infinite',
          }}
        >
          {isComplete ? (
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" strokeWidth="2.5">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          ) : isFailed ? (
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-danger)" strokeWidth="2.5">
              <circle cx="12" cy="12" r="10" />
              <line x1="15" y1="9" x2="9" y2="15" />
              <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
          ) : (
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-indigo-light)" strokeWidth="2" className="animate-spin">
              <path d="M21 12a9 9 0 1 1-6.219-8.56" />
            </svg>
          )}
        </div>

        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
          {isComplete ? 'Validation Complete!' : isFailed ? 'Validation Failed' : 'Validating Agent...'}
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 14 }}>
          {status?.current_step || 'Preparing validation pipeline...'}
        </p>
      </div>

      {/* Error State */}
      {isFailed && (
        <div className="alert alert-error animate-fade-in" style={{ marginBottom: 24 }}>
          <span style={{ fontSize: 18 }}>⚠</span>
          <div>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Validation Failed</div>
            <div style={{ fontSize: 13 }}>{error || status?.error_message}</div>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {!isFailed && (
        <div className="card animate-fade-in animate-delay-100" style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12, fontSize: 13 }}>
            <span style={{ fontWeight: 600, color: 'var(--color-text-secondary)' }}>Progress</span>
            <span style={{ fontWeight: 700, color: 'var(--color-indigo-light)' }}>{progress}%</span>
          </div>
          <div className="progress-bar" style={{ height: 8, marginBottom: 24 }}>
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>

          {/* Step List */}
          <div className="step-list">
            {STEPS.map((step, i) => {
              const isDone = i < currentStepIdx || isComplete;
              const isActive = i === currentStepIdx && !isComplete && !isFailed;
              const isPending = i > currentStepIdx && !isComplete;

              return (
                <div
                  key={step.key}
                  className="step-item"
                  style={{
                    opacity: isPending ? 0.4 : 1,
                    transition: 'opacity 0.3s',
                  }}
                >
                  <div
                    className={`step-dot ${isDone ? 'step-dot-complete' : isActive ? 'step-dot-active' : 'step-dot-pending'}`}
                  />
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        fontSize: 13,
                        fontWeight: isActive ? 600 : 500,
                        color: isDone
                          ? 'var(--color-success)'
                          : isActive
                          ? 'var(--color-text-primary)'
                          : 'var(--color-text-muted)',
                      }}
                    >
                      {step.label}
                    </div>
                    {isActive && (
                      <div style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: 2 }}>
                        {step.desc}
                      </div>
                    )}
                  </div>
                  {isDone && (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" strokeWidth="2.5">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Run ID */}
      <div
        className="animate-fade-in animate-delay-200"
        style={{ textAlign: 'center', fontSize: 12, color: 'var(--color-text-muted)' }}
      >
        Run ID: <code style={{ fontFamily: 'monospace', color: 'var(--color-text-secondary)' }}>{id}</code>
      </div>
    </div>
  );
}
