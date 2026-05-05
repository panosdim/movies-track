from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.movie import Movie as MovieModel
from app.models.movie import MovieProvider as MovieProviderModel
from app.schemas.movie import Movie, MovieCreate, MovieUpdate, MovieProviderSchema

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=list[Movie])
def get_movies(
    skip: int = 0,
    limit: int = 100,
    user_id: str | None = Query(default=None, description="Filter by user email"),
    watched: bool | None = Query(default=None, description="Filter by watched status"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of movies, optionally filtered by user and watched status."""
    q = db.query(MovieModel)
    if user_id is not None:
        q = q.filter(MovieModel.user_id == user_id)
    if watched is not None:
        q = q.filter(MovieModel.watched == watched)
    return q.offset(skip).limit(limit).all()


@router.get("/{movie_id}", response_model=Movie)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """Return a single movie entry by its primary key id."""
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.post("/", response_model=Movie, status_code=201)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    """Add a new movie entry."""
    db_movie = MovieModel(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


@router.put("/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, movie: MovieUpdate, db: Session = Depends(get_db)):
    """Update an existing movie entry (partial update supported)."""
    db_movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    for field, value in movie.model_dump(exclude_unset=True).items():
        setattr(db_movie, field, value)
    db.commit()
    db.refresh(db_movie)
    return db_movie


@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """Delete a movie entry and its providers."""
    db_movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(db_movie)
    db.commit()


# --- Providers sub-resource ---

@router.get("/{movie_id}/providers", response_model=list[MovieProviderSchema])
def get_providers(movie_id: int, db: Session = Depends(get_db)):
    """Return all streaming providers for a movie."""
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie.providers


@router.post("/{movie_id}/providers", response_model=MovieProviderSchema, status_code=201)
def add_provider(
    movie_id: int, provider: MovieProviderSchema, db: Session = Depends(get_db)
):
    """Add a streaming provider to a movie."""
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    db_provider = MovieProviderModel(
        movie_id=movie_id,
        logo_path=provider.logo_path,
        provider_name=provider.provider_name,
    )
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider


@router.delete("/{movie_id}/providers/{provider_name}", status_code=204)
def delete_provider(movie_id: int, provider_name: str, db: Session = Depends(get_db)):
    """Remove a streaming provider from a movie."""
    db_provider = (
        db.query(MovieProviderModel)
        .filter(
            MovieProviderModel.movie_id == movie_id,
            MovieProviderModel.provider_name == provider_name,
        )
        .first()
    )
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    db.delete(db_provider)
    db.commit()
