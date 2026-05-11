"""Database queries for the recommender using SQLAlchemy."""

import logging

from app.database import SESSIONLOCAL
from app.models.movie import Movie

_logger = logging.getLogger(__name__)


def get_movie_ratings(user_id: str) -> tuple[list[int], list[float]]:
    """
    Fetch movie IDs and normalised ratings for a user.

    Unrated movies (rating is None or 0) receive a neutral placeholder of 0.5 (2.5/5).

    Returns:
        Tuple of (movie_ids, normalised_ratings).
    """
    db = SESSIONLOCAL()
    try:
        rows = (
            db.query(Movie.movie_id, Movie.rating)
            .filter(Movie.user_id == user_id)
            .all()
        )
    except (AttributeError, ValueError) as e:
        _logger.error("Error fetching movie ratings for user %s: %s", user_id, e)
        return [], []
    finally:
        db.close()

    movie_ids: list[int] = []
    ratings: list[float] = []

    for movie_id, rating in rows:
        movie_ids.append(movie_id)
        if rating is not None and rating > 0:
            ratings.append(rating / 5.0)
        else:
            ratings.append(2.5 / 5.0)

    return movie_ids, ratings


def get_movie_ids(user_id: str) -> list[int]:
    """
    Retrieve all TMDb movie IDs in a user's list.

    Returns:
        List of movie_id integers.
    """
    db = SESSIONLOCAL()
    try:
        rows = db.query(Movie.movie_id).filter(Movie.user_id == user_id).all()
    except (AttributeError, ValueError) as e:
        _logger.error("Error fetching movie IDs for user %s: %s", user_id, e)
        return []
    finally:
        db.close()

    return [row[0] for row in rows]
