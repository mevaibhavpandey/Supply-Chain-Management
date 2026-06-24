import os
import uuid
import zipfile
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from database import get_db
from models import ValidationRun
from schemas import SubmitUrlRequest, SubmitResponse
from config import settings
from engine.orchestrator import run_validation_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()

def get_run_storage_path(run_id: str) -> str:
    path = os.path.join(settings.storage_path, run_id)
    os.makedirs(path, exist_ok=True)
    return path

@router.post("/submit/url", response_model=SubmitResponse)
async def submit_url(
    request: SubmitUrlRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    run_id = str(uuid.uuid4())

    run = ValidationRun(
        id=run_id,
        agent_name=request.agent_name,
        submission_type="repo_url",
        submission_url=request.repo_url,
        files_path=get_run_storage_path(run_id),
        status="pending",
        progress=0,
        current_step="Queued for validation",
        scm_use_case=request.scm_use_case,
        description=request.description,
        expected_input=request.expected_input,
        expected_output=request.expected_output,
        enable_llm=request.enable_llm,
    )
    db.add(run)
    await db.commit()

    background_tasks.add_task(run_validation_pipeline, run_id, "repo_url", request.repo_url, None)

    logger.info(f"Submitted repo URL validation job: {run_id}")
    return SubmitResponse(run_id=run_id, status="pending", message="Validation job queued successfully")

@router.post("/submit/files", response_model=SubmitResponse)
async def submit_files(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    agent_name: str = Form(...),
    scm_use_case: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    expected_input: Optional[str] = Form(None),
    expected_output: Optional[str] = Form(None),
    enable_llm: bool = Form(False),
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one file must be uploaded")

    run_id = str(uuid.uuid4())
    storage_path = get_run_storage_path(run_id)
    upload_dir = os.path.join(storage_path, "uploaded")
    os.makedirs(upload_dir, exist_ok=True)

    for upload_file in files:
        file_path = os.path.join(upload_dir, upload_file.filename)
        with open(file_path, "wb") as f:
            content = await upload_file.read()
            f.write(content)

        # If it is a ZIP, extract it
        if upload_file.filename.endswith(".zip"):
            extract_dir = os.path.join(storage_path, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            with zipfile.ZipFile(file_path, "r") as zf:
                zf.extractall(extract_dir)

    submission_type = "zip" if any(f.filename.endswith(".zip") for f in files) else "files"

    run = ValidationRun(
        id=run_id,
        agent_name=agent_name,
        submission_type=submission_type,
        files_path=storage_path,
        status="pending",
        progress=0,
        current_step="Queued for validation",
        scm_use_case=scm_use_case,
        description=description,
        expected_input=expected_input,
        expected_output=expected_output,
        enable_llm=enable_llm,
    )
    db.add(run)
    await db.commit()

    background_tasks.add_task(run_validation_pipeline, run_id, submission_type, None, storage_path)

    logger.info(f"Submitted file upload validation job: {run_id}")
    return SubmitResponse(run_id=run_id, status="pending", message="Validation job queued successfully")
