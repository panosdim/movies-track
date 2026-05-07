import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import auth, movies, tmdb

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Movies Recommendations API",
    description="Backend API for movie recommendations",
    version="0.1.0",
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


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("Application startup complete")
    try:
        from app.database import engine
        # Test database connection
        with engine.connect() as conn:
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


@app.get("/api/v1/health")
def health_check():
    """Return the health status of the API."""
    return {"status": "ok"}
