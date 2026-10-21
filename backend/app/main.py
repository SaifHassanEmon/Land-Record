import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import settings
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("land_records")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: directory setup, database initialization."""
    logger.info("Initializing Bangladesh Land Records Digitization System...")

    # 1. Ensure required folders exist
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.DEMO_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory verified: {settings.UPLOAD_DIR.resolve()}")
    logger.info(f"Demo docs directory verified: {settings.DEMO_DOCS_DIR.resolve()}")

    # 2. Initialize database tables
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)

    yield

    logger.info("Application shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Bangladesh Land Records Digitization System with EasyOCR, OpenCV, and Bengali Unicode extraction.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
base_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://land-record-delta.vercel.app",
]
if isinstance(settings.CORS_ORIGINS, list):
    origins = list(set(base_origins + settings.CORS_ORIGINS))
else:
    origins = list(set(base_origins + [settings.CORS_ORIGINS]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers under /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get(
    "/",
    tags=["Root"],
    summary="Root Status",
    description="Basic system status and metadata.",
)
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    status_code=status.HTTP_200_OK,
)
def health_check():
    return {
        "status": "healthy",
        "upload_dir_exists": settings.UPLOAD_DIR.exists(),
        "demo_docs_dir_exists": settings.DEMO_DOCS_DIR.exists(),
    }
