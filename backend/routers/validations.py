from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging

from database import get_db
from models import ValidationRun, TrustScore, Finding, Recommendation, Evidence, AIInsight
from schemas import (
    ValidationStatusResponse, ValidationResultResponse, ResultSummary,
    ScoreBreakdown, FindingSchema, RecommendationSchema, EvidenceSchema, AIInsightSchema
)

logger = logging.getLogger(__name__)
router = APIRouter()

DIMENSION_DISPLAY = {
    "specification_completeness": "Specification Completeness",
    "io_clarity": "Input / Output Clarity",
    "reliability": "Reliability & Error Handling",
    "security": "Security Hygiene",
    "observability": "Observability / Logging",
    "scm_readiness": "SCM Readiness / Business Fit",
    "overall": "Overall Trust Score",
}

DIMENSION_WEIGHTS = {
    "specification_completeness": 0.20,
    "io_clarity": 0.15,
    "reliability": 0.20,
    "security": 0.20,
    "observability": 0.10,
    "scm_readiness": 0.15,
}

VERDICT_COLOR = {
    "Production Ready": "#10b981",
    "Demo Ready": "#6366f1",
    "Conditionally Ready": "#f59e0b",
    "High Risk": "#f97316",
    "Critical Risk": "#ef4444",
}

@router.get("/validations/{run_id}/status", response_model=ValidationStatusResponse)
async def get_validation_status(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ValidationRun).where(ValidationRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Validation run not found")

    return ValidationStatusResponse(
        run_id=run.id,
        status=run.status,
        progress=run.progress,
        current_step=run.current_step,
        created_at=run.created_at,
        completed_at=run.completed_at,
        error_message=run.error_message
    )

@router.get("/validations/{run_id}/results", response_model=ValidationResultResponse)
async def get_validation_results(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ValidationRun).where(ValidationRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Validation run not found")
    if run.status != "complete":
        raise HTTPException(status_code=400, detail=f"Validation is not complete. Current status: {run.status}")

    scores_result = await db.execute(select(TrustScore).where(TrustScore.run_id == run_id))
    scores = scores_result.scalars().all()

    findings_result = await db.execute(select(Finding).where(Finding.run_id == run_id))
    findings = findings_result.scalars().all()

    recs_result = await db.execute(select(Recommendation).where(Recommendation.run_id == run_id))
    recommendations = recs_result.scalars().all()

    evidence_result = await db.execute(select(Evidence).where(Evidence.run_id == run_id))
    evidence_items = evidence_result.scalars().all()

    insights_result = await db.execute(select(AIInsight).where(AIInsight.run_id == run_id))
    insights = insights_result.scalars().all()

    overall_score_obj = next((s for s in scores if s.dimension == "overall"), None)
    overall_score = overall_score_obj.score if overall_score_obj else 0.0

    if overall_score >= 81:
        verdict = "Production Ready"
    elif overall_score >= 61:
        verdict = "Demo Ready"
    elif overall_score >= 41:
        verdict = "Conditionally Ready"
    elif overall_score >= 21:
        verdict = "High Risk"
    else:
        verdict = "Critical Risk"

    evidence_by_finding = {}
    for ev in evidence_items:
        if ev.finding_id:
            if ev.finding_id not in evidence_by_finding:
                evidence_by_finding[ev.finding_id] = []
            evidence_by_finding[ev.finding_id].append(ev.id)

    critical = sum(1 for f in findings if f.severity == "Critical")
    high = sum(1 for f in findings if f.severity == "High")

    summary = ResultSummary(
        agent_name=run.agent_name,
        run_id=run.id,
        timestamp=run.completed_at.isoformat() if run.completed_at else run.created_at.isoformat(),
        overall_trust_score=round(overall_score, 1),
        verdict=verdict,
        verdict_color=VERDICT_COLOR.get(verdict, "#6366f1"),
        submission_type=run.submission_type,
        scm_use_case=run.scm_use_case,
        total_findings=len(findings),
        critical_findings=critical,
        high_findings=high,
    )

    score_breakdown = []
    for s in scores:
        if s.dimension != "overall":
            pct = (s.score / s.max_score) * 100 if s.max_score > 0 else 0
            score_breakdown.append(ScoreBreakdown(
                dimension=s.dimension,
                display_name=DIMENSION_DISPLAY.get(s.dimension, s.dimension),
                score=round(s.score, 1),
                max_score=s.max_score,
                percentage=round(pct, 1),
                remarks=s.remarks or "",
                weight=DIMENSION_WEIGHTS.get(s.dimension, 0.0)
            ))

    findings_schema = []
    for f in findings:
        findings_schema.append(FindingSchema(
            id=f.id,
            rule_id=f.rule_id,
            severity=f.severity,
            category=f.category,
            title=f.title,
            description=f.description,
            why_it_matters=f.why_it_matters,
            score_impact=f.score_impact,
            dimension=f.dimension,
            evidence_refs=evidence_by_finding.get(f.id, [])
        ))

    recs_schema = [RecommendationSchema(
        id=r.id, finding_id=r.finding_id, title=r.title,
        recommendation=r.recommendation, implementation_guidance=r.implementation_guidance,
        priority=r.priority, expected_impact=r.expected_impact, impacted_dimension=r.impacted_dimension
    ) for r in recommendations]

    evidence_schema = [EvidenceSchema(
        id=e.id, finding_id=e.finding_id, file_path=e.file_path,
        line_start=e.line_start, line_end=e.line_end, snippet=e.snippet, reason=e.reason
    ) for e in evidence_items]

    insights_schema = [AIInsightSchema(id=i.id, insight_type=i.insight_type, content=i.content) for i in insights]

    return ValidationResultResponse(
        summary=summary,
        score_breakdown=score_breakdown,
        findings=findings_schema,
        recommendations=recs_schema,
        evidence=evidence_schema,
        ai_insights=insights_schema
    )

@router.delete("/validations/{run_id}")
async def delete_validation(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ValidationRun).where(ValidationRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Validation run not found")
    await db.delete(run)
    await db.commit()
    return {"message": "Validation run deleted successfully"}
