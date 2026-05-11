"""Scheduled component to check for watch provider changes and send email notifications."""

import logging
import threading
import time

import schedule
from sqlalchemy.orm import Session

from app.database import SESSIONLOCAL
from app.models.movie import Movie, MovieProvider
from app.services.email_service import send_summary_notification
from app.services.watch_provider_service import fetch_movie_watch_providers_batch

logger = logging.getLogger(__name__)


def _providers_to_dict(providers: list) -> dict:
    """Convert list of provider dicts to a dict keyed by provider_name for comparison."""
    result = {}
    for p in providers:
        result[p["provider_name"]] = p
    return result


def _providers_changed(old_providers: list, new_providers: list) -> bool:
    """Check if the provider lists have changed."""
    old_dict = _providers_to_dict(old_providers)
    new_dict = _providers_to_dict(new_providers)
    return old_dict != new_dict


def check_watch_provider_changes():
    """Check all unwatched movies for provider changes and send per-user summary emails."""
    logger.info("Starting scheduled check for watch provider changes")

    db: Session = SESSIONLOCAL()
    try:
        # Get all unwatched movies with their current providers
        unwatched_movies = (
            db.query(Movie)
            .filter(Movie.watched.isnot(True), Movie.movie_id.isnot(None))
            .all()
        )

        if not unwatched_movies:
            logger.info("No unwatched movies to check")
            return

        # Collect TMDb movie IDs for batch fetching
        tmdb_ids = [m.movie_id for m in unwatched_movies if m.movie_id]
        new_providers_map = fetch_movie_watch_providers_batch(tmdb_ids)

        # Group changed movies by user
        user_changes = {}
        changed_count = 0

        for movie in unwatched_movies:
            if not movie.movie_id:
                continue

            new_providers = new_providers_map.get(movie.movie_id, [])
            current_providers = movie.providers if movie.providers else []

            if _providers_changed(current_providers, new_providers):
                # Update providers in DB
                db.query(MovieProvider).filter(
                    MovieProvider.movie_id == movie.id
                ).delete()

                for p in new_providers:
                    new_provider = MovieProvider(
                        movie_id=movie.id,
                        provider_name=p["provider_name"],
                        logo_path=p["logo_path"],
                    )
                    db.add(new_provider)

                # Group by user for email notification
                user_email = movie.user_id
                if user_email:
                    if user_email not in user_changes:
                        user_changes[user_email] = []
                    user_changes[user_email].append(
                        {
                            "title": movie.title,
                            "poster": movie.poster,
                            "providers": new_providers,
                        }
                    )
                    changed_count += 1

        db.commit()

        # Send per-user summary emails
        for user_email, movies in user_changes.items():
            try:
                send_summary_notification(user_email, movies)
            except Exception as e:
                logger.error("Failed to send summary email to %s: %s", user_email, e)

        logger.info(
            "Provider check completed: %d movies changed across %d users",
            changed_count,
            len(user_changes),
        )

    except Exception as e:
        logger.error("Error during provider check: %s", e)
        db.rollback()
    finally:
        db.close()


def clear_watched_providers():
    """Clear provider info from watched movies."""
    logger.info("Clearing provider info from watched movies")
    db: Session = SESSIONLOCAL()
    try:
        watched_movies = db.query(Movie).filter(Movie.watched.is_(True)).all()
        for movie in watched_movies:
            db.query(MovieProvider).filter(MovieProvider.movie_id == movie.id).delete()
        db.commit()
        logger.info("Cleared providers for %d watched movies", len(watched_movies))
    except Exception as e:
        logger.error("Error clearing watched providers: %s", e)
        db.rollback()
    finally:
        db.close()


def _run_provider_scheduler():
    """Run the provider check scheduler in a background thread."""
    cron_time = "00:00"  # Midnight daily
    schedule.every().day.at(cron_time).do(check_watch_provider_changes)
    logger.info(
        "Provider scheduler started: check_watch_provider_changes scheduled daily at %s",
        cron_time,
    )

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except RuntimeError as e:
            logger.error("Provider scheduler error: %s", e)


def start_provider_scheduler():
    """Start the watch provider check scheduler as a daemon thread."""
    provider_thread = threading.Thread(target=_run_provider_scheduler, daemon=True)
    provider_thread.start()
    logger.info("Provider scheduler thread started")
