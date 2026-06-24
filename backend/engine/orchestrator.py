"""
Validation Pipeline Orchestrator

This module coordinates the complete validation workflow:
  Step 1: Ingest the agent (clone repo or read uploaded files)
  Step 2: Static analysis (detect files, languages, patterns)
  Step 3: Rule engine (run 18 deterministic checks)
  Step 4: Scoring engine (calculate weighted trust scores)
  Step 5: Evidence builder (map findings to code locations)
  Step 6: Recommendation builder (generate actionable fixes)
  Step 7: LLM insights (optional AI commentary)
  Step 8: Persist results to database
"""

import asyncio
import logging
import uuid
import os
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import settings
from database import AsyncSessionLocal
from models import ValidationRun, TrustScore, Finding, Recommendation, Evidence, AIInsight
from engine.repo_ingestor import RepoIngestor
from engine.static_analyzer import StaticAnalyzer
from engine.rule_engine import RuleEngine
from engine.scoring_engine import ScoringEngine
from engine.evidence_builder import EvidenceBuilder
from engine.recommendation_builder import RecommendationBuilder
from engine.llm_insights import LLMInsightsEngine

logger = logging.getLogger(__name__)

# Use the centralized database session factory (configured for PostgreSQL/SQLite with SSL support)
_bg_session_factory = AsyncSessionLocal


async def _update_run_status(
    session: AsyncSession,
    run_id: str,
    status: str,
    progress: int,
    current_step: str,
    error_message: Optional[str] = None
):
    """Update the status of a validation run in the database."""
    result = await session.execute(select(ValidationRun).where(ValidationRun.id == run_id))
    run = result.scalar_one_or_none()
    if run:
        run.status = status
        run.progress = progress
        run.current_step = current_step
        if error_message:
            run.error_message = error_message
        if status in ("complete", "failed"):
            run.completed_at = datetime.utcnow()
        await session.commit()
    logger.info(f"[{run_id}] Status: {status} ({progress}%) — {current_step}")


async def run_validation_pipeline(
    run_id: str,
    submission_type: str,
    repo_url: Optional[str],
    storage_path: Optional[str],
):
    """
    Main validation pipeline. Runs as a FastAPI background task.

    Args:
        run_id: UUID of the ValidationRun record
        submission_type: 'repo_url' | 'zip' | 'files'
        repo_url: GitHub/GitLab URL (for repo_url type)
        storage_path: Local path where uploaded files are stored
    """
    logger.info(f"[{run_id}] Starting validation pipeline. type={submission_type}")

    async with _bg_session_factory() as session:
        try:
            # ── Fetch run metadata ──────────────────────────────────────
            result = await session.execute(select(ValidationRun).where(ValidationRun.id == run_id))
            run = result.scalar_one_or_none()
            if not run:
                logger.error(f"[{run_id}] ValidationRun not found in DB!")
                return

            agent_name = run.agent_name
            enable_llm = run.enable_llm
            scm_use_case = run.scm_use_case

            # ── Step 1: Ingest ──────────────────────────────────────────
            await _update_run_status(session, run_id, "running", 5, "Ingesting agent source...")

            ingestor = RepoIngestor(run_id=run_id, storage_path=run.files_path or storage_path or "")

            if submission_type == "repo_url" and repo_url:
                try:
                    local_path = await ingestor.ingest_url(repo_url)
                except Exception as e:
                    await _update_run_status(
                        session, run_id, "failed", 0, "Ingestion failed",
                        error_message=f"Failed to clone repository: {str(e)}"
                    )
                    return
            elif submission_type == "zip":
                extracted_path = os.path.join(run.files_path or "", "extracted")
                if os.path.exists(extracted_path):
                    local_path = ingestor.find_actual_root(extracted_path)
                else:
                    local_path = os.path.join(run.files_path or "", "uploaded")
            else:
                local_path = os.path.join(run.files_path or "", "uploaded")

            if not local_path or not os.path.exists(local_path):
                await _update_run_status(
                    session, run_id, "failed", 0, "Source files not found",
                    error_message=f"Could not locate agent source at: {local_path}"
                )
                return

            # ── Step 2: Static Analysis ─────────────────────────────────
            await _update_run_status(session, run_id, "running", 20, "Running static analysis...")
            await asyncio.sleep(0.1)

            profile = ingestor.ingest_directory(local_path)
            profile.agent_name = agent_name
            profile.submission_type = submission_type
            profile.scm_use_case = scm_use_case
            profile.description = run.description
            profile.expected_input = run.expected_input
            profile.expected_output = run.expected_output

            analyzer = StaticAnalyzer()
            profile = analyzer.analyze(profile)

            logger.info(
                f"[{run_id}] Analysis complete: {profile.file_count} files, "
                f"lang={profile.detected_language}, fw={profile.detected_framework}"
            )

            # ── Step 3: Rule Engine ─────────────────────────────────────
            await _update_run_status(session, run_id, "running", 40, "Running validation rules...")
            await asyncio.sleep(0.1)

            rule_engine = RuleEngine()
            findings = rule_engine.run_all_checks(profile)
            logger.info(f"[{run_id}] Rule engine: {len(findings)} findings")

            # ── Step 4: Scoring ─────────────────────────────────────────
            await _update_run_status(session, run_id, "running", 60, "Calculating trust score...")

            scoring_engine = ScoringEngine()
            overall_score, verdict, dimension_scores = scoring_engine.calculate(profile, findings)
            logger.info(f"[{run_id}] Score: {overall_score}/100 — {verdict}")

            # ── Step 5: Evidence ────────────────────────────────────────
            await _update_run_status(session, run_id, "running", 70, "Gathering evidence...")
            evidence_builder = EvidenceBuilder()
            evidence_items = evidence_builder.build(profile, findings)

            # ── Step 6: Recommendations ─────────────────────────────────
            await _update_run_status(session, run_id, "running", 80, "Building recommendations...")
            rec_builder = RecommendationBuilder()
            recommendations = rec_builder.build(findings)

            # ── Step 7: LLM Insights (optional) ─────────────────────────
            ai_insights = []
            if enable_llm and settings.llm_enabled:
                await _update_run_status(session, run_id, "running", 88, "Generating AI insights...")
                findings_summary = "\n".join([
                    f"- [{f.severity}] {f.title} (impact: -{f.score_impact}pts)"
                    for f in findings[:10]
                ])
                llm_engine = LLMInsightsEngine()
                ai_insights = await llm_engine.generate_insights(
                    agent_name=agent_name,
                    overall_score=overall_score,
                    verdict=verdict,
                    scm_use_case=scm_use_case,
                    findings_summary=findings_summary,
                    enable_llm=True,
                )

            # ── Step 8: Persist results ─────────────────────────────────
            await _update_run_status(session, run_id, "running", 92, "Saving results...")

            # Save dimension scores
            for ds in dimension_scores:
                score_record = TrustScore(
                    id=str(uuid.uuid4()),
                    run_id=run_id,
                    dimension=ds.dimension,
                    score=ds.score,
                    max_score=ds.max_score,
                    remarks=ds.remarks,
                )
                session.add(score_record)

            # Save overall score
            session.add(TrustScore(
                id=str(uuid.uuid4()),
                run_id=run_id,
                dimension="overall",
                score=overall_score,
                max_score=100.0,
                remarks=f"Verdict: {verdict}",
            ))

            # Save findings
            for f in findings:
                finding_record = Finding(
                    id=f.id,
                    run_id=run_id,
                    rule_id=f.rule_id,
                    severity=f.severity,
                    category=f.category,
                    title=f.title,
                    description=f.description,
                    why_it_matters=f.why_it_matters,
                    score_impact=f.score_impact,
                    dimension=f.dimension,
                )
                session.add(finding_record)

            # Save evidence
            for ev in evidence_items:
                evidence_record = Evidence(
                    id=ev["id"],
                    run_id=run_id,
                    finding_id=ev.get("finding_id"),
                    file_path=ev["file_path"],
                    line_start=ev.get("line_start"),
                    line_end=ev.get("line_end"),
                    snippet=ev.get("snippet"),
                    reason=ev["reason"],
                )
                session.add(evidence_record)

            # Save recommendations
            for rec in recommendations:
                rec_record = Recommendation(
                    id=rec["id"],
                    run_id=run_id,
                    finding_id=rec["finding_id"],
                    title=rec["title"],
                    recommendation=rec["recommendation"],
                    implementation_guidance=rec.get("implementation_guidance"),
                    priority=rec["priority"],
                    expected_impact=rec["expected_impact"],
                    impacted_dimension=rec.get("impacted_dimension"),
                )
                session.add(rec_record)

            # Save AI insights
            for insight in ai_insights:
                insight_record = AIInsight(
                    id=insight["id"],
                    run_id=run_id,
                    insight_type=insight["insight_type"],
                    content=insight["content"],
                )
                session.add(insight_record)

            await session.commit()

            # Mark complete
            await _update_run_status(session, run_id, "complete", 100, "Validation complete")
            logger.info(f"[{run_id}] Pipeline complete. score={overall_score} verdict={verdict}")

        except Exception as e:
            logger.exception(f"[{run_id}] Pipeline failed with unhandled exception: {e}")
            try:
                await _update_run_status(
                    session, run_id, "failed", 0,
                    "Validation failed — internal error",
                    error_message=str(e)
                )
            except Exception as inner_e:
                logger.error(f"[{run_id}] Could not update failure status: {inner_e}")
