"""Recommender router for movie suggestions."""

import logging
import os

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from app.recommender.database import get_movie_ids
from app.recommender.cache import get_suggestions_cache, set_suggestions_cache
from app.recommender.model_utils import get_model_path, compute_user_suggestions
from app.routers.tmdb import fetch_new_releases
from app.utils.security import get_current_user_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommender", tags=["recommender"])


@router.get("/suggestions")
async def suggestions(
    max_suggestions: int = 20,
    authorization: str | None = Header(default=None),
):
    """Get personalized movie suggestions for the authenticated user."""
    user_id = get_current_user_email(authorization)
    model_path = get_model_path(user_id)

    if not model_path or not os.path.exists(model_path):
        logger.info(
            "No model found for user %s. Returning generic new releases.", user_id
        )
        try:
            releases_1 = fetch_new_releases(1) or []
            releases_2 = fetch_new_releases(2) or []
            new_releases = releases_1 + releases_2

            watchlist_movie_ids = get_movie_ids(user_id)
            filtered_movies = [
                movie
                for movie in new_releases
                if movie["id"] not in watchlist_movie_ids
            ]

            return JSONResponse(
                status_code=200,
                content=filtered_movies[:max_suggestions],
            )
        except (IOError, OSError, ValueError) as e:
            logger.error(
                "Failed to fetch generic suggestions for user %s: %s", user_id, e
            )
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Could not fetch generic suggestions.",
                },
            )

    cached_suggestions = get_suggestions_cache(user_id)
    if cached_suggestions is not None:
        logger.info("Returning cached suggestions for user: %s", user_id)
        return JSONResponse(
            status_code=200,
            content=cached_suggestions[:max_suggestions],
        )

    logger.info("Computing suggestions for user: %s (not in cache)", user_id)
    suggestions_list = compute_user_suggestions(user_id)

    if not suggestions_list:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": (
                    f"No suggestions available for user {user_id}. "
                    "Please ensure the model is trained."
                ),
            },
        )

    set_suggestions_cache(user_id, suggestions_list)

    return JSONResponse(status_code=200, content=suggestions_list[:max_suggestions])
