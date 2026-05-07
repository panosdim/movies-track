from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.movie import Movie as MovieModel
from app.schemas.movie import Movie
from app.utils.jwt_token import verify_token

router = APIRouter(prefix="/movies", tags=["movies"])


def get_current_user_email(authorization: str | None = None) -> str:
    """Extract and verify user email from Bearer token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return user_email


@router.get("/watched", response_model=list[Movie])
def get_watched_movies(
    authorization: str | None = None,
    db: Session = Depends(get_db),
):
    """Get all movies marked as watched by the current user."""
    user_email = get_current_user_email(authorization)
    movies = (
        db.query(MovieModel)
        .filter(MovieModel.user_id == user_email, MovieModel.watched == True)
        .all()
    )
    return movies


@router.get("/watchlist", response_model=list[Movie])
def get_watchlist(
    authorization: str | None = None,
    db: Session = Depends(get_db),
):
    """Get all movies in the watchlist (not watched) for the current user."""
    user_email = get_current_user_email(authorization)
    movies = (
        db.query(MovieModel)
        .filter(
            MovieModel.user_id == user_email,
            (MovieModel.watched == False) | (MovieModel.watched.is_(None)),
        )
        .all()
    )
    return movies


@router.post("/", response_model=Movie, status_code=200)
def add_movie(
    movie_data: dict,
    authorization: str | None = None,
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
    return new_movie


@router.post("/watched/{movie_id}", response_model=Movie, status_code=200)
def set_watched(
    movie_id: int,
    authorization: str | None = None,
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
    authorization: str | None = None,
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
    return movie


@router.delete("/{movie_id}", status_code=204)
def delete_movie(
    movie_id: int,
    authorization: str | None = None,
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

    db.delete(movie)
    db.commit()
