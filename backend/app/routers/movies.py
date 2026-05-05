from fastapi import APIRouter
from app.schemas.movie import Movie, MovieCreate

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=list[Movie])
def get_movies():
    """Return a list of movie recommendations."""
    return []


@router.get("/{movie_id}", response_model=Movie)
def get_movie(movie_id: int):
    """Return a single movie by ID."""
    return Movie(id=movie_id, title="Example Movie", genre="Drama", rating=8.5, description="A placeholder movie.")


@router.post("/", response_model=Movie, status_code=201)
def create_movie(movie: MovieCreate):
    """Add a new movie recommendation."""
    return Movie(id=1, **movie.model_dump())
