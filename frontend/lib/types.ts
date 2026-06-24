export interface SubmitUrlRequest {
  agent_name: string
  repo_url: string
  scm_use_case?: string
  description?: string
  expected_input?: string
  expected_output?: string
  enable_llm?: boolean
}

export interface SubmitResponse {
  run_id: string
  status: string
  message: string
}

export interface ValidationStatus {
  run_id: string
  status: 'pending' | 'running' | 'complete' | 'failed'
  progress: number
  current_step: string
  created_at: string
  completed_at?: string
  error_message?: string
}

export interface ScoreBreakdown {
  dimension: string
  display_name: string
  score: number
  max_score: number
  percentage: number
  remarks: string
  weight: number
}

export interface Finding {
  id: string
  rule_id: string
  severity: 'Critical' | 'High' | 'Medium' | 'Low'
  category: string
  title: string
  description: string
  why_it_matters: string
  score_impact: number
  dimension: string
  evidence_refs: string[]
}

export interface Recommendation {
  id: string
  finding_id: string
  title: string
  recommendation: string
  implementation_guidance?: string
  priority: string
  expected_impact: string
  impacted_dimension?: string
}

export interface Evidence {
  id: string
  finding_id?: string
  file_path: string
  line_start?: number
  line_end?: number
  snippet?: string
  reason: string
}

export interface AIInsight {
  id: string
  insight_type: string
  content: string
}

export interface ResultSummary {
  agent_name: string
  run_id: string
  timestamp: string
  overall_trust_score: number
  verdict: string
  verdict_color: string
  submission_type: string
  scm_use_case?: string
  total_findings: number
  critical_findings: number
  high_findings: number
}

export interface ValidationResult {
  summary: ResultSummary
  score_breakdown: ScoreBreakdown[]
  findings: Finding[]
  recommendations: Recommendation[]
  evidence: Evidence[]
  ai_insights: AIInsight[]
}

export interface HistoryItem {
  id: string
  agent_name: string
  submission_type: string
  status: string
  overall_score?: number
  verdict?: string
  total_findings: number
  created_at: string
  completed_at?: string
  scm_use_case?: string
}
