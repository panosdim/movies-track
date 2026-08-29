"""FastAPI application entrypoint for the Movies Track backend."""

import logging
import os
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import engine
from app.routers import auth, movies, tmdb, recommender
from app.recommender.model_utils import start_background_threads
from app.services.watch_provider_scheduler import start_provider_scheduler

load_dotenv()

# Configure logging: console + rotating file (200MB x 5 backups) under LOG_DIR
LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
_log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=_log_format,
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            os.path.join(LOG_DIR, "app.log"),
            maxBytes=200 * 1024 * 1024,
            backupCount=5,
        ),
    ],
)

# Get logger for this module
_logger = logging.getLogger(__name__)
_logger.debug("Logging is configured.")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Log application lifespan events."""

    _logger.info("Starting up API...")
    try:
        with engine.connect():
            _logger.info("Database connection successful")
    except (IOError, OSError, RuntimeError) as exception:
        _logger.error("Database connection failed: %s", exception)
        raise

    # Start recommender background threads (training worker + daily scheduler)
    try:
        start_background_threads()
    except (ImportError, RuntimeError, AttributeError) as e:
        _logger.warning("Failed to start recommender background threads: %s", e)

    # Start watch provider change checker (daily midnight)
    try:
        start_provider_scheduler()
    except RuntimeError as e:
        _logger.warning("Failed to start provider scheduler: %s", e)

    yield
    _logger.info("Shutting down API...")


app = FastAPI(
    title="Movies Recommendations API",
    description="Backend API for movie recommendations and tracking",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 endpoints (all under /api/v1)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(movies.router, prefix="/api/v1")
app.include_router(tmdb.router, prefix="/api/v1")
app.include_router(recommender.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health_check():
    """Return the health status of the API."""
    return {"status": "ok"}
