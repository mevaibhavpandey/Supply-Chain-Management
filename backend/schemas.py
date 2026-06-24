from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

# ---- Submission Schemas ----

class SubmitUrlRequest(BaseModel):
    agent_name: str = Field(..., min_length=1, max_length=200)
    repo_url: str = Field(..., description="GitHub/GitLab repository URL")
    scm_use_case: Optional[str] = None
    description: Optional[str] = None
    expected_input: Optional[str] = None
    expected_output: Optional[str] = None
    enable_llm: bool = False

class SubmitResponse(BaseModel):
    run_id: str
    status: str
    message: str

# ---- Status Schemas ----

class ValidationStatusResponse(BaseModel):
    run_id: str
    status: str
    progress: int
    current_step: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

# ---- Result Schemas ----

class ScoreBreakdown(BaseModel):
    dimension: str
    display_name: str
    score: float
    max_score: float
    percentage: float
    remarks: str
    weight: float

class FindingSchema(BaseModel):
    id: str
    rule_id: str
    severity: str
    category: str
    title: str
    description: str
    why_it_matters: str
    score_impact: float
    dimension: str
    evidence_refs: List[str] = []

class RecommendationSchema(BaseModel):
    id: str
    finding_id: str
    title: str
    recommendation: str
    implementation_guidance: Optional[str] = None
    priority: str
    expected_impact: str
    impacted_dimension: Optional[str] = None

class EvidenceSchema(BaseModel):
    id: str
    finding_id: Optional[str] = None
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    snippet: Optional[str] = None
    reason: str

class AIInsightSchema(BaseModel):
    id: str
    insight_type: str
    content: str

class ResultSummary(BaseModel):
    agent_name: str
    run_id: str
    timestamp: str
    overall_trust_score: float
    verdict: str
    verdict_color: str
    submission_type: str
    scm_use_case: Optional[str] = None
    total_findings: int
    critical_findings: int
    high_findings: int

class ValidationResultResponse(BaseModel):
    summary: ResultSummary
    score_breakdown: List[ScoreBreakdown]
    findings: List[FindingSchema]
    recommendations: List[RecommendationSchema]
    evidence: List[EvidenceSchema]
    ai_insights: List[AIInsightSchema]

# ---- History Schemas ----

class HistoryItem(BaseModel):
    id: str
    agent_name: str
    submission_type: str
    status: str
    overall_score: Optional[float] = None
    verdict: Optional[str] = None
    total_findings: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    scm_use_case: Optional[str] = None

class HistoryResponse(BaseModel):
    runs: List[HistoryItem]
    total: int
    page: int
    per_page: int
