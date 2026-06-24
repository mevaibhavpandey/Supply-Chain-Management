// API client for the AI Trust Validator backend
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {}
    throw new APIError(res.status, detail);
  }
  return res.json();
}

// ── Submit by URL ────────────────────────────────────────────────────────────
export interface SubmitUrlPayload {
  agent_name: string;
  repo_url: string;
  scm_use_case?: string;
  description?: string;
  expected_input?: string;
  expected_output?: string;
  enable_llm?: boolean;
}

export async function submitUrl(payload: SubmitUrlPayload) {
  return request<{ run_id: string; status: string; message: string }>('/api/v1/submit/url', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// ── Submit by Files ──────────────────────────────────────────────────────────
export async function submitFiles(formData: FormData) {
  const res = await fetch(`${API_BASE}/api/v1/submit/files`, {
    method: 'POST',
    body: formData,
    // Don't set Content-Type; browser sets multipart/form-data with boundary automatically
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {}
    throw new APIError(res.status, detail);
  }
  return res.json() as Promise<{ run_id: string; status: string; message: string }>;
}

// ── Validation Status ─────────────────────────────────────────────────────────
export interface ValidationStatus {
  run_id: string;
  status: 'pending' | 'running' | 'complete' | 'failed';
  progress: number;
  current_step: string;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export async function getValidationStatus(runId: string): Promise<ValidationStatus> {
  return request<ValidationStatus>(`/api/v1/validations/${runId}/status`);
}

// ── Validation Results ────────────────────────────────────────────────────────
export interface ScoreBreakdown {
  dimension: string;
  display_name: string;
  score: number;
  max_score: number;
  percentage: number;
  remarks: string;
  weight: number;
}

export interface Finding {
  id: string;
  rule_id: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  category: string;
  title: string;
  description: string;
  why_it_matters: string;
  score_impact: number;
  dimension: string;
  evidence_refs: string[];
}

export interface Recommendation {
  id: string;
  finding_id: string;
  title: string;
  recommendation: string;
  implementation_guidance?: string;
  priority: string;
  expected_impact: string;
  impacted_dimension?: string;
}

export interface Evidence {
  id: string;
  finding_id?: string;
  file_path: string;
  line_start?: number;
  line_end?: number;
  snippet?: string;
  reason: string;
}

export interface AIInsight {
  id: string;
  insight_type: string;
  content: string;
}

export interface ResultSummary {
  agent_name: string;
  run_id: string;
  timestamp: string;
  overall_trust_score: number;
  verdict: string;
  verdict_color: string;
  submission_type: string;
  scm_use_case?: string;
  total_findings: number;
  critical_findings: number;
  high_findings: number;
}

export interface ValidationResult {
  summary: ResultSummary;
  score_breakdown: ScoreBreakdown[];
  findings: Finding[];
  recommendations: Recommendation[];
  evidence: Evidence[];
  ai_insights: AIInsight[];
}

export async function getValidationResults(runId: string): Promise<ValidationResult> {
  return request<ValidationResult>(`/api/v1/validations/${runId}/results`);
}

// ── History ───────────────────────────────────────────────────────────────────
export interface HistoryItem {
  id: string;
  agent_name: string;
  submission_type: string;
  status: string;
  overall_score?: number;
  verdict?: string;
  total_findings: number;
  created_at: string;
  completed_at?: string;
  scm_use_case?: string;
}

export interface HistoryResponse {
  runs: HistoryItem[];
  total: number;
  page: number;
  per_page: number;
}

export async function getHistory(page = 1, perPage = 20): Promise<HistoryResponse> {
  return request<HistoryResponse>(`/api/v1/history?page=${page}&per_page=${perPage}`);
}

export async function deleteValidation(runId: string) {
  return request(`/api/v1/validations/${runId}`, { method: 'DELETE' });
}
