'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { submitUrl, submitFiles, APIError } from '@/lib/api';

const SCM_USE_CASES = [
  'Inventory Optimization',
  'Demand Forecasting',
  'Purchase Order Automation',
  'Supplier Selection & Evaluation',
  'Logistics & Shipment Tracking',
  'Warehouse Management',
  'Supply Chain Risk Monitoring',
  'Contract Management',
  'Quality Control & Returns',
  'Other',
];

export default function SubmitPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [mode, setMode] = useState<'url' | 'files'>('url');
  const [dragOver, setDragOver] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [files, setFiles] = useState<File[]>([]);

  const [form, setForm] = useState({
    agent_name: '',
    repo_url: '',
    scm_use_case: '',
    description: '',
    expected_input: '',
    expected_output: '',
    enable_llm: false,
  });

  const update = (k: string, v: string | boolean) =>
    setForm((prev) => ({ ...prev, [k]: v }));

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...dropped]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles((prev) => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (i: number) => {
    setFiles((prev) => prev.filter((_, idx) => idx !== i));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!form.agent_name.trim()) {
      setError('Agent name is required.');
      return;
    }

    if (mode === 'url' && !form.repo_url.trim()) {
      setError('Repository URL is required.');
      return;
    }

    if (mode === 'files' && files.length === 0) {
      setError('Please upload at least one file.');
      return;
    }

    setSubmitting(true);
    try {
      let run_id: string;

      if (mode === 'url') {
        const res = await submitUrl({
          agent_name: form.agent_name,
          repo_url: form.repo_url,
          scm_use_case: form.scm_use_case || undefined,
          description: form.description || undefined,
          expected_input: form.expected_input || undefined,
          expected_output: form.expected_output || undefined,
          enable_llm: form.enable_llm,
        });
        run_id = res.run_id;
      } else {
        const fd = new FormData();
        fd.append('agent_name', form.agent_name);
        if (form.scm_use_case) fd.append('scm_use_case', form.scm_use_case);
        if (form.description) fd.append('description', form.description);
        if (form.expected_input) fd.append('expected_input', form.expected_input);
        if (form.expected_output) fd.append('expected_output', form.expected_output);
        fd.append('enable_llm', String(form.enable_llm));
        files.forEach((f) => fd.append('files', f));
        const res = await submitFiles(fd);
        run_id = res.run_id;
      }

      router.push(`/validating/${run_id}`);
    } catch (err) {
      setError(err instanceof APIError ? err.message : 'Submission failed. Please try again.');
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: '48px 24px' }}>
      {/* Header */}
      <div className="animate-fade-in" style={{ marginBottom: 40 }}>
        <div style={{ marginBottom: 12 }}>
          <span className="feature-badge">🔬 Deterministic Scoring</span>
        </div>
        <h1 className="page-title" style={{ fontSize: 32, marginBottom: 8 }}>
          Submit Agent for Validation
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 15 }}>
          Provide your agent via GitHub URL or file upload. Get a full trust report in under 30 seconds.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="animate-fade-in animate-delay-100">
        {/* Input Mode Toggle */}
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="form-group" style={{ marginBottom: 24 }}>
            <label className="form-label">Submission Method</label>
            <div className="tab-group">
              <button
                type="button"
                className={`tab ${mode === 'url' ? 'active' : ''}`}
                onClick={() => setMode('url')}
                id="tab-url"
              >
                🔗 Repository URL
              </button>
              <button
                type="button"
                className={`tab ${mode === 'files' ? 'active' : ''}`}
                onClick={() => setMode('files')}
                id="tab-files"
              >
                📂 Upload Files / ZIP
              </button>
            </div>
          </div>

          {/* Agent Name */}
          <div className="form-group" style={{ marginBottom: 20 }}>
            <label className="form-label" htmlFor="agent-name">
              Agent Name <span style={{ color: 'var(--color-danger)' }}>*</span>
            </label>
            <input
              id="agent-name"
              className="form-input"
              placeholder="e.g. ProcurementAutomationAgent v2.1"
              value={form.agent_name}
              onChange={(e) => update('agent_name', e.target.value)}
              required
            />
          </div>

          {/* URL or File Upload */}
          {mode === 'url' ? (
            <div className="form-group">
              <label className="form-label" htmlFor="repo-url">
                Repository URL <span style={{ color: 'var(--color-danger)' }}>*</span>
              </label>
              <input
                id="repo-url"
                className="form-input"
                placeholder="https://github.com/org/repo"
                value={form.repo_url}
                onChange={(e) => update('repo_url', e.target.value)}
                type="url"
              />
              <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
                Supports GitHub, GitLab, Bitbucket, and any public git URL
              </span>
            </div>
          ) : (
            <div className="form-group">
              <label className="form-label">Upload Files</label>
              <div
                className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleFileDrop}
                onClick={() => fileInputRef.current?.click()}
                id="upload-zone"
              >
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" strokeWidth="1.5" style={{ margin: '0 auto 12px', display: 'block' }}>
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <p style={{ fontWeight: 600, marginBottom: 4 }}>Drop files here or click to browse</p>
                <p style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>
                  .py, .js, .ts, .go, .zip — max 50MB
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".py,.js,.ts,.tsx,.jsx,.go,.java,.rb,.zip,.yaml,.yml,.toml,.json,.md,.txt,.env"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                  id="file-input"
                />
              </div>
              {files.length > 0 && (
                <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {files.map((f, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '8px 12px',
                        background: 'var(--color-bg-secondary)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border)',
                        fontSize: 13,
                      }}
                    >
                      <span style={{ color: 'var(--color-text-secondary)' }}>
                        📄 {f.name}
                        <span style={{ marginLeft: 8, color: 'var(--color-text-muted)' }}>
                          ({(f.size / 1024).toFixed(0)} KB)
                        </span>
                      </span>
                      <button
                        type="button"
                        onClick={() => removeFile(i)}
                        className="btn btn-ghost btn-sm"
                        style={{ color: 'var(--color-danger)' }}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Metadata */}
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ fontWeight: 700, marginBottom: 20, fontSize: 15 }}>
            Agent Metadata <span style={{ color: 'var(--color-text-muted)', fontWeight: 400 }}>(optional — improves analysis accuracy)</span>
          </h3>

          <div className="form-group" style={{ marginBottom: 16 }}>
            <label className="form-label" htmlFor="scm-use-case">SCM Use Case</label>
            <select
              id="scm-use-case"
              className="form-input form-select"
              value={form.scm_use_case}
              onChange={(e) => update('scm_use_case', e.target.value)}
            >
              <option value="">Select use case...</option>
              {SCM_USE_CASES.map((u) => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 16 }}>
            <label className="form-label" htmlFor="description">Agent Description</label>
            <textarea
              id="description"
              className="form-input form-textarea"
              placeholder="What does this agent do? What problem does it solve?"
              value={form.description}
              onChange={(e) => update('description', e.target.value)}
            />
          </div>

          <div className="grid-2" style={{ gap: 16 }}>
            <div className="form-group">
              <label className="form-label" htmlFor="expected-input">Expected Input Format</label>
              <textarea
                id="expected-input"
                className="form-input form-textarea"
                placeholder='e.g. { "order_id": "PO-123", "quantity": 500 }'
                value={form.expected_input}
                onChange={(e) => update('expected_input', e.target.value)}
                style={{ minHeight: 80 }}
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="expected-output">Expected Output Format</label>
              <textarea
                id="expected-output"
                className="form-input form-textarea"
                placeholder='e.g. { "status": "submitted", "confirmation_id": "..." }'
                value={form.expected_output}
                onChange={(e) => update('expected_output', e.target.value)}
                style={{ minHeight: 80 }}
              />
            </div>
          </div>
        </div>

        {/* LLM Toggle */}
        <div className="card" style={{ marginBottom: 32 }}>
          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 16,
              cursor: 'pointer',
            }}
            htmlFor="enable-llm"
          >
            <div style={{ position: 'relative' }}>
              <input
                id="enable-llm"
                type="checkbox"
                checked={form.enable_llm}
                onChange={(e) => update('enable_llm', e.target.checked)}
                style={{ opacity: 0, width: 0, height: 0, position: 'absolute' }}
              />
              <div
                style={{
                  width: 44,
                  height: 24,
                  background: form.enable_llm ? 'var(--color-indigo)' : 'var(--color-bg-input)',
                  borderRadius: 12,
                  border: '1px solid var(--color-border)',
                  transition: 'background 0.2s',
                  cursor: 'pointer',
                  position: 'relative',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    top: 3,
                    left: form.enable_llm ? 22 : 3,
                    width: 16,
                    height: 16,
                    background: '#fff',
                    borderRadius: '50%',
                    transition: 'left 0.2s',
                  }}
                />
              </div>
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14 }}>Enable AI Insights (Optional)</div>
              <div style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 2 }}>
                Adds GPT-powered business risk commentary. Does NOT affect the trust score. Requires API key.
              </div>
            </div>
          </label>
        </div>

        {/* Error */}
        {error && (
          <div className="alert alert-error animate-fade-in" style={{ marginBottom: 20 }}>
            <span>⚠</span>
            <span>{error}</span>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          className="btn btn-primary btn-lg"
          disabled={submitting}
          style={{ width: '100%', justifyContent: 'center' }}
          id="submit-btn"
        >
          {submitting ? (
            <>
              <div
                className="animate-spin"
                style={{
                  width: 16,
                  height: 16,
                  border: '2px solid rgba(255,255,255,0.3)',
                  borderTop: '2px solid white',
                  borderRadius: '50%',
                }}
              />
              Submitting...
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
              Start Validation
            </>
          )}
        </button>
      </form>
    </div>
  );
}
