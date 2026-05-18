"""Movies router for managing user movie lists, watchlist, and ratings."""

import logging

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.movie import Movie as MovieModel, MovieProvider
from app.schemas.movie import Movie
from app.utils.security import get_current_user_email
from app.utils.tmdb import TMDB_API_KEY, TMDB_BASE_URL
from app.recommender.model_utils import process_training_request
from app.services.watch_provider_service import fetch_watch_providers

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/watched", response_model=list[Movie])
def get_watched_movies(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Get all movies marked as watched by the current user."""
    user_email = get_current_user_email(authorization)
    movies = (
        db.query(MovieModel)
        .options(joinedload(MovieModel.providers))
        .filter(MovieModel.user_id == user_email, MovieModel.watched.is_(True))
        .all()
    )
    return movies


@router.get("/watchlist", response_model=list[Movie])
def get_watchlist(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Get all movies in the watchlist (not watched) for the current user, enriched with TMDb voteAverage."""
    user_email = get_current_user_email(authorization)
    movies = (
        db.query(MovieModel)
        .options(joinedload(MovieModel.providers))
        .filter(
            MovieModel.user_id == user_email,
            MovieModel.watched.isnot(True) | MovieModel.watched.is_(None),
        )
        .all()
    )

    # Enrich with TMDb voteAverage if API key is configured
    vote_averages: dict[int, float] = {}
    if TMDB_API_KEY:
        tmdb_ids = [m.movie_id for m in movies if m.movie_id]
        if tmdb_ids:
            vote_averages = _fetch_vote_averages(tmdb_ids)

    return [
        Movie.model_validate(movie).model_copy(
            update={"vote_average": vote_averages.get(movie.movie_id) if movie.movie_id else None}
        )
        for movie in movies
    ]


def _fetch_vote_averages(tmdb_ids: list) -> dict:
    """Fetch vote_average for multiple movies from TMDb."""
    results = {}
    for movie_id in tmdb_ids:
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{TMDB_BASE_URL}/movie/{movie_id}",
                    headers={"Authorization": f"Bearer {TMDB_API_KEY}"},
                )
                if response.status_code == 200:
                    data = response.json()
                    results[movie_id] = data.get("vote_average")
        except httpx.HTTPError:
            pass
    return results


@router.post("/", response_model=Movie, status_code=200)
def add_movie(
    movie_data: dict,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Add a new movie to the user's list."""
    user_email = get_current_user_email(authorization)

    # Validate required fields
    required_fields = ["movieId", "title", "poster"]
    for field in required_fields:
        if field not in movie_data or movie_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}",
            )

    # Create new movie entry
    new_movie = MovieModel(
        movie_id=movie_data.get("movieId"),
        title=movie_data.get("title"),
        poster=movie_data.get("poster"),
        user_id=user_email,
        watched=False,
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)

    # Fetch and store watch providers from TMDb (GR region)
    tmdb_movie_id = movie_data.get("movieId")
    if tmdb_movie_id:
        try:
            providers = fetch_watch_providers(tmdb_movie_id)
            for provider in providers:
                new_provider = MovieProvider(
                    movie_id=new_movie.id,
                    provider_name=provider["provider_name"],
                    logo_path=provider["logo_path"],
                )
                db.add(new_provider)
            db.commit()
            db.refresh(new_movie)
        except Exception as e:
            logger.error("Failed to fetch watch providers for movie %s: %s", tmdb_movie_id, e)

    try:
        process_training_request(user_email)
    except (RuntimeError, ValueError, IOError) as e:
        logger.error("Error triggering retrain after add_movie: %s", e)

    return new_movie


@router.post("/watched/{movie_id}", response_model=Movie, status_code=200)
def set_watched(
    movie_id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Mark a movie as watched."""
    user_email = get_current_user_email(authorization)
    movie = (
        db.query(MovieModel)
        .filter(MovieModel.id == movie_id, MovieModel.user_id == user_email)
        .first()
    )

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    movie.watched = True
    db.commit()
    db.refresh(movie)
    return movie


@router.post("/rate/{movie_id}", response_model=Movie, status_code=200)
def set_rating(
    movie_id: int,
    rating_data: dict,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Set a rating for a movie (0-5)."""
    user_email = get_current_user_email(authorization)

    # Validate rating
    if "rating" not in rating_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: rating",
        )

    rating = rating_data.get("rating")
    if not isinstance(rating, int) or rating < 0 or rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be an integer between 0 and 5",
        )

    movie = (
        db.query(MovieModel)
        .filter(MovieModel.id == movie_id, MovieModel.user_id == user_email)
        .first()
    )

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    movie.rating = rating
    db.commit()
    db.refresh(movie)

    try:
        process_training_request(user_email)
    except (RuntimeError, ValueError, IOError) as e:
        logger.error("Error triggering retrain after set_rating: %s", e)

    return movie


@router.delete("/{movie_id}", status_code=204)
def delete_movie(
    movie_id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Delete a movie from the user's list."""
    user_email = get_current_user_email(authorization)
    movie = (
        db.query(MovieModel)
        .filter(MovieModel.id == movie_id, MovieModel.user_id == user_email)
        .first()
    )

    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    try:
        process_training_request(user_email)
    except (RuntimeError, ValueError, IOError) as e:
        logger.error("Error triggering retrain after delete_movie: %s", e)

    db.delete(movie)
    db.commit()
