"""Caching utilities for user data and movie suggestions."""

import logging
import time

_logger = logging.getLogger(__name__)

# User data cache
USER_DATA_CACHE: dict[str, dict] = {}
USER_DATA_CACHE_TTL = 7200  # 2 hours
USER_DATA_TIMESTAMPS: dict[str, float] = {}

# Suggestions cache
SUGGESTIONS_CACHE: dict[str, list] = {}
SUGGESTIONS_CACHE_TTL = 86400  # 1 day (24 hours)
SUGGESTIONS_TIMESTAMPS: dict[str, float] = {}


def get_suggestions_cache(user_id: str) -> list | None:
    """Get cached suggestions if valid"""
    current_time = time.time()

    if (
        user_id in SUGGESTIONS_CACHE
        and user_id in SUGGESTIONS_TIMESTAMPS
        and current_time - SUGGESTIONS_TIMESTAMPS[user_id] < SUGGESTIONS_CACHE_TTL
    ):
        return SUGGESTIONS_CACHE[user_id]

    return None


def set_suggestions_cache(user_id: str, suggestions: list):
    """Cache suggestions for a user"""
    SUGGESTIONS_CACHE[user_id] = suggestions
    SUGGESTIONS_TIMESTAMPS[user_id] = time.time()
    _logger.info("Cached %d suggestions for user: %s", len(suggestions), user_id)


def get_user_data_cache(user_id: str) -> dict | None:
    """Get cached user data (genre_list, actor_list, director_list) if valid"""
    current_time = time.time()

    if (
        user_id in USER_DATA_CACHE
        and user_id in USER_DATA_TIMESTAMPS
        and current_time - USER_DATA_TIMESTAMPS[user_id] < USER_DATA_CACHE_TTL
    ):
        return USER_DATA_CACHE[user_id]

    return None


def set_user_data_cache(
    user_id: str,
    genre_list: list[str],
    actor_list: list[str],
    director_list: list[str],
    num_movies: int,
    movie_ids: list[int],
    ratings: list[float],
):
    """Cache user data"""
    USER_DATA_CACHE[user_id] = {
        "genre_list": genre_list,
        "actor_list": actor_list,
        "director_list": director_list,
        "num_movies": num_movies,
        "movie_ids": movie_ids,
        "ratings": ratings,
    }
    USER_DATA_TIMESTAMPS[user_id] = time.time()


def invalidate_caches(user_id: str):
    """Invalidate all caches for a user"""
    if user_id in USER_DATA_CACHE:
        del USER_DATA_CACHE[user_id]
    if user_id in USER_DATA_TIMESTAMPS:
        del USER_DATA_TIMESTAMPS[user_id]
    if user_id in SUGGESTIONS_CACHE:
        del SUGGESTIONS_CACHE[user_id]
    if user_id in SUGGESTIONS_TIMESTAMPS:
        del SUGGESTIONS_TIMESTAMPS[user_id]
    _logger.info("Invalidated caches for user: %s", user_id)
