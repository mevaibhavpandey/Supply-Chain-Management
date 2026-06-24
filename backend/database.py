from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings
import os

# Ensure data directory exists
os.makedirs("./data", exist_ok=True)
os.makedirs(settings.storage_path, exist_ok=True)

db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

if db_url.startswith("postgresql+asyncpg://") and "ssl=" not in db_url:
    db_url += ("&" if "?" in db_url else "?") + "ssl=require"


engine_args = {}
if db_url.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(
    db_url,
    echo=False,
    **engine_args
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

import asyncio
import logging

db_logger = logging.getLogger(__name__)

async def create_tables():
    retries = 6
    delay = 5
    for attempt in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            db_logger.info("Database tables created/verified successfully.")
            return
        except Exception as e:
            if attempt == retries:
                db_logger.critical("Could not connect to database. All retries exhausted.")
                raise e
            db_logger.warning(
                f"Database connection attempt {attempt} failed: {e}. Retrying in {delay} seconds..."
            )
            await asyncio.sleep(delay)

