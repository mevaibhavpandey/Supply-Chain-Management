from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from database import create_tables
from routers import submissions, validations, history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Trust Validator API...")
    await create_tables()
    logger.info("Database tables created/verified.")
    yield
    logger.info("Shutting down AI Trust Validator API.")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Universal AI Agent Validation and Trust Assessment Platform",
    lifespan=lifespan
)

allow_origins = settings.cors_origins
allow_credentials = True
if "*" in allow_origins or (len(allow_origins) == 1 and allow_origins[0] == "*"):
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submissions.router, prefix="/api/v1", tags=["Submissions"])
app.include_router(validations.router, prefix="/api/v1", tags=["Validations"])
app.include_router(history.router, prefix="/api/v1", tags=["History"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}

@app.get("/")
async def root():
    return {"message": "AI Trust Validator API", "docs": "/docs"}
