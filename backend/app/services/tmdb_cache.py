"""TMDb API response cache with TTL-based expiration."""

import logging
import time
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# Cache TTL in seconds (1 hour)
DEFAULT_TTL = 3600

# Simple in-memory cache: {movie_id: {"data": ..., "timestamp": ...}}
_cache: dict[int, dict[str, Any]] = {}


def get_cached(movie_id: int, ttl: int = DEFAULT_TTL) -> dict | None:
    """Get cached TMDb response for a movie, or None if expired/missing."""
    entry = _cache.get(movie_id)
    if entry is None:
        return None

    if time.time() - entry["timestamp"] > ttl:
        del _cache[movie_id]
        return None

    return entry["data"]


def set_cached(movie_id: int, data: dict) -> None:
    """Cache a TMDb response for a movie."""
    _cache[movie_id] = {
        "data": data,
        "timestamp": time.time(),
    }


def clear_cache() -> None:
    """Clear all cached entries."""
    _cache.clear()
    logger.info("TMDb cache cleared")


def clear_expired(ttl: int = DEFAULT_TTL) -> int:
    """Remove expired entries. Returns number of entries removed."""
    now = time.time()
    expired = [k for k, v in _cache.items() if now - v["timestamp"] > ttl]
    for k in expired:
        del _cache[k]
    if expired:
        logger.info("Cleared %d expired TMDb cache entries", len(expired))
    return len(expired)
