"""TMDb API router for movie search, autocomplete, popular movies, and recommender utilities."""

import logging
import os

import httpx
from fastapi import APIRouter, HTTPException, status

router = APIRouter(tags=["tmdb"])

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

_logger = logging.getLogger(__name__)


def fetch_movie_details(tmdb_id):
    """Fetch detailed movie information from TMDb for the given TMDb ID."""
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}?append_to_response=credits"
    try:
        with httpx.Client() as client:
            response = client.get(
                url,
                headers={"Authorization": f"Bearer {TMDB_API_KEY}"},
            )
            response.raise_for_status()
            data = response.json()

            return {
                "genres": [genre["name"] for genre in data.get("genres", [])],
                "release_year": int(data.get("release_date", "0000").split("-")[0]),
                "duration": data.get("runtime", 0),
                "popularity": data.get("popularity", 0),
                "average_rating": data.get("vote_average", 0),
                "actors": [
                    cast["name"] for cast in data.get("credits", {}).get("cast", [])[:5]
                ],
                "director": [
                    crew["name"]
                    for crew in data.get("credits", {}).get("crew", [])
                    if crew["job"] == "Director"
                ],
            }
    except httpx.HTTPError:
        _logger.error("Failed to fetch data for TMDb ID: %s", tmdb_id)
        return None


def fetch_new_releases(page=1):
    """Fetch new movie releases from TMDb."""
    url = f"{TMDB_BASE_URL}/movie/now_playing"
    try:
        with httpx.Client() as client:
            response = client.get(
                url,
                params={"page": page},
                headers={"Authorization": f"Bearer {TMDB_API_KEY}"},
            )
            response.raise_for_status()
            data = response.json()

            return [
                {
                    "poster_path": movie.get("poster_path", ""),
                    "release_date": movie.get("release_date", ""),
                    "id": movie.get("id"),
                    "title": movie.get("title", ""),
                    "score": movie.get("vote_average"),
                }
                for movie in data.get("results", [])
            ]
    except httpx.HTTPError:
        _logger.error("Failed to fetch new releases for page %s", page)
        return None


@router.post("/search")
def search_movies(search_data: dict):
    """Search for movies on TMDb by title."""
    if not TMDB_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TMDb API key not configured",
        )

    term = search_data.get("term")
    if not term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: term",
        )

    try:
        with httpx.Client() as client:
            response = client.get(
                f"{TMDB_BASE_URL}/search/movie",
                params={"query": term},
                headers={"Authorization": f"Bearer {TMDB_API_KEY}"},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TMDb API error: {str(e)}",
        ) from e


@router.post("/autocomplete")
def autocomplete_movies(search_data: dict):
    """Autocomplete endpoint — returns array of [title, release_date, poster_path] tuples."""
    if not TMDB_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TMDb API key not configured",
        )

    term = search_data.get("term")
    if not term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: term",
        )

    try:
        with httpx.Client() as client:
            response = client.get(
                f"{TMDB_BASE_URL}/search/movie",
                params={"query": term},
                headers={"Authorization": f"Bearer {TMDB_API_KEY}"},
            )
            response.raise_for_status()
            data = response.json()

            # Format results as [title, release_date, poster_url]
            results = []
            for movie in data.get("results", []):
                title = movie.get("title")
                release_date = movie.get("release_date")
                poster_path = movie.get("poster_path")

                if title and poster_path:
                    poster_url = (
                        f"https://image.tmdb.org/t/p/w45_and_h67_bestv2{poster_path}"
                    )
                    results.append([title, release_date, poster_url])

            return results
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TMDb API error: {str(e)}",
        ) from e


@router.get("/popular")
def get_popular_movies():
    """Get popular movies from TMDb."""
    if not TMDB_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TMDb API key not configured",
        )

    try:
        with httpx.Client() as client:
            response = client.get(
                f"{TMDB_BASE_URL}/movie/popular",
                headers={"Authorization": f"Bearer {TMDB_API_KEY}"},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TMDb API error: {str(e)}",
        ) from e
