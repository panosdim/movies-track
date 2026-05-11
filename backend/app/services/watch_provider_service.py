"""Watch provider info service for fetching and managing streaming providers from TMDb."""

import logging
import os

import httpx

logger = logging.getLogger(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Cached flatrate (subscription) providers for GR region
_flatrate_providers_cache = None


def _get_flatrate_providers():
    """Fetch flatrate (subscription) providers for GR region with caching."""
    global _flatrate_providers_cache
    if _flatrate_providers_cache is not None:
        return _flatrate_providers_cache

    if not TMDB_API_KEY:
        logger.warning("TMDb API key not configured, cannot fetch providers")
        return {}

    try:
        with httpx.Client() as client:
            response = client.get(
                f"{TMDB_BASE_URL}/watch/providers/movie",
                headers={"Authorization": f"Bearer {TMDB_API_KEY}"},
            )
            response.raise_for_status()
            data = response.json()

            # Build a mapping of provider_id -> {provider_name, logo_path}
            providers = {}
            for provider_id, info in data.get("providers", {}).get("flatrate", {}).items():
                # Note: TMDb v3 watch/providers returns a dict with different structure
                if isinstance(info, dict):
                    providers[info.get("id", provider_id)] = {
                        "provider_name": info.get("provider_name", ""),
                        "logo_path": info.get("logo_path", ""),
                    }

            _flatrate_providers_cache = providers
            return providers

    except httpx.HTTPError as e:
        logger.error("Failed to fetch flatrate providers: %s", e)
        return {}


def fetch_watch_providers(tmdb_movie_id: int) -> list:
    """Fetch watch providers for a specific movie in GR region from TMDb."""
    if not TMDB_API_KEY:
        logger.warning("TMDb API key not configured, cannot fetch watch providers")
        return []

    try:
        with httpx.Client() as client:
            response = client.get(
                f"{TMDB_BASE_URL}/movie/{tmdb_movie_id}/watch/providers",
                headers={"Authorization": f"Bearer {TMDB_API_KEY}"},
            )
            response.raise_for_status()
            data = response.json()

            providers = []

            # Get flatrate (subscription) providers for GR region
            gr_providers = data.get("results", {}).get("GR", {})
            flatrate = gr_providers.get("flatrate", [])
            rent = gr_providers.get("rent", [])

            # Prioritize flatrate, then rent
            all_providers = flatrate + rent
            for provider in all_providers:
                providers.append({
                    "provider_name": provider.get("provider_name", ""),
                    "logo_path": provider.get("logo_path", ""),
                })

            return providers

    except httpx.HTTPError as e:
        logger.error("Failed to fetch watch providers for movie %s: %s", tmdb_movie_id, e)
        return []


def fetch_movie_watch_providers_batch(movie_ids: list) -> dict:
    """Fetch watch providers for multiple movies at once.
    Returns dict mapping movie_id -> list of providers.
    """
    if not TMDB_API_KEY or not movie_ids:
        return {}

    results = {}
    for movie_id in movie_ids:
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers",
                    headers={"Authorization": f"Bearer {TMDB_API_KEY}"},
                )
                response.raise_for_status()
                data = response.json()

                providers = []
                gr_providers = data.get("results", {}).get("GR", {})
                flatrate = gr_providers.get("flatrate", [])
                rent = gr_providers.get("rent", [])

                for provider in flatrate + rent:
                    providers.append({
                        "provider_name": provider.get("provider_name", ""),
                        "logo_path": provider.get("logo_path", ""),
                    })

                results[movie_id] = providers

        except httpx.HTTPError as e:
            logger.error("Failed to fetch watch providers for movie %s: %s", movie_id, e)
            results[movie_id] = []

    return results
