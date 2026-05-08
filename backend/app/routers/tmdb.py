"""TMDb API router for movie search, autocomplete, and popular movies."""

import os
import httpx
from fastapi import APIRouter, HTTPException, status

router = APIRouter(tags=["tmdb"])

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"


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
