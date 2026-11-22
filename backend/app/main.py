from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine
from app.core.logging import logger
import app.mcp_servers  # Register all 7 MCP servers


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🏛️ Starting AICTE NEXUS Enterprise Platform...")
    # Verify DB connectivity on startup
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("✅ PostgreSQL Database connection verified successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")

    yield

    logger.info("🏛️ Shutting down AICTE NEXUS Platform...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Institution Complaint Monitoring & Coordination Platform - AICTE (Ministry of Education, Govt. of India)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if isinstance(settings.ALLOWED_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_and_logging(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(process_time)
    response.headers["X-Government-Platform"] = "AICTE-NEXUS-SIH26264"
    return response


# Include Core API v1
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"])
async def health_check():
    db_status = "UNKNOWN"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "HEALTHY"
    except Exception as e:
        db_status = f"UNHEALTHY: {str(e)}"

    return {
        "status": "OPERATIONAL" if db_status == "HEALTHY" else "DEGRADED",
        "service": "AICTE Nexus API",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "organization": "All India Council for Technical Education (AICTE)",
        "sih_problem": "SIH26264",
        "api_docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
        "status": "ONLINE",
    }

