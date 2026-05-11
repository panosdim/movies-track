"""FastAPI application entrypoint for the Movies Track backend."""

import logging
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import engine
from app.routers import auth, movies, tmdb, recommender
from app.recommender.model_utils import start_background_threads

load_dotenv()

# Use Uvicorn's logger for application info and error logging
logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Log application lifespan events."""

    logger.info("Starting up API...")
    try:
        with engine.connect():
            logger.info("Database connection successful")
    except (IOError, OSError, RuntimeError) as exception:
        logger.error("Database connection failed: %s", exception)
        raise

    # Start recommender background threads (training worker + daily scheduler)
    try:
        start_background_threads()
    except (ImportError, RuntimeError, AttributeError) as e:
        logger.warning("Failed to start recommender background threads: %s", e)

    yield
    logger.info("Shutting down API...")


app = FastAPI(
    title="Movies Recommendations API",
    description="Backend API for movie recommendations",
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
