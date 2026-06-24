from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
import logging

from database import get_db
from models import ValidationRun, TrustScore, Finding
from schemas import HistoryResponse, HistoryItem

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/history", response_model=HistoryResponse)
async def get_history(
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None)
):
    query = select(ValidationRun).order_by(desc(ValidationRun.created_at))
    if status:
        query = query.where(ValidationRun.status == status)

    count_query = select(func.count(ValidationRun.id))
    if status:
        count_query = count_query.where(ValidationRun.status == status)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * per_page
    runs_result = await db.execute(query.offset(offset).limit(per_page))
    runs = runs_result.scalars().all()

    items = []
    for run in runs:
        score_result = await db.execute(
            select(TrustScore).where(TrustScore.run_id == run.id, TrustScore.dimension == "overall")
        )
        score = score_result.scalar_one_or_none()

        findings_count = await db.execute(
            select(func.count(Finding.id)).where(Finding.run_id == run.id)
        )

        overall = score.score if score else None
        verdict = None
        if overall is not None:
            if overall >= 81:
                verdict = "Production Ready"
            elif overall >= 61:
                verdict = "Demo Ready"
            elif overall >= 41:
                verdict = "Conditionally Ready"
            elif overall >= 21:
                verdict = "High Risk"
            else:
                verdict = "Critical Risk"

        items.append(HistoryItem(
            id=run.id,
            agent_name=run.agent_name,
            submission_type=run.submission_type,
            status=run.status,
            overall_score=round(overall, 1) if overall is not None else None,
            verdict=verdict,
            total_findings=findings_count.scalar() or 0,
            created_at=run.created_at,
            completed_at=run.completed_at,
            scm_use_case=run.scm_use_case,
        ))

    return HistoryResponse(runs=items, total=total, page=page, per_page=per_page)
