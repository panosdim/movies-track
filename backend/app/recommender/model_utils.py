"""Model utilities for training and computing movie recommendations."""

import glob
import json
import logging
import os
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import schedule
from tensorflow.keras.models import load_model

from app.recommender.cache import (
    set_suggestions_cache,
    get_user_data_cache,
    set_user_data_cache,
    invalidate_caches,
)
from app.recommender.database import get_movie_ids, get_movie_ratings
from app.recommender.preprocess import preprocess_movie_data
from app.recommender.recommendation_model import build_model, train_model
from app.routers.tmdb import fetch_movie_details, fetch_new_releases

_logger = logging.getLogger(__name__)


# Models are expected to be mounted into the container at /app/recommender/models.
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Training queue and worker setup
training_queue = queue.Queue()


def get_model_path(user_id: str) -> str:
    """Get the full path for a user's model file"""
    return os.path.join(MODELS_DIR, f"{user_id}.keras")


def get_model_metadata_path(user_id: str) -> str:
    """Get the full path for a user's model metadata file."""
    return os.path.join(MODELS_DIR, f"{user_id}_metadata.json")


def save_model_metadata(user_id: str, metadata: dict):
    """Saves model metadata to a file."""
    metadata_path = get_model_metadata_path(user_id)
    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f)
        _logger.info("Saved model metadata for user %s to %s", user_id, metadata_path)
    except (IOError, OSError, json.JSONDecodeError) as e:
        _logger.error("Failed to save model metadata for user %s: %s", user_id, e)


def load_model_metadata(user_id: str) -> dict | None:
    """Loads model metadata from a file."""
    metadata_path = get_model_metadata_path(user_id)
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            _logger.info(
                "Loaded model metadata for user %s from %s", user_id, metadata_path
            )
            return metadata
    except FileNotFoundError:
        _logger.warning(
            "Metadata file not found for user %s at %s", user_id, metadata_path
        )
        return None
    except (IOError, OSError, json.JSONDecodeError) as e:
        _logger.error("Failed to load model metadata for user %s: %s", user_id, e)
        return None


def get_all_user_ids() -> list[str]:
    """Get all user IDs by checking existing keras model files"""
    try:
        keras_pattern = os.path.join(MODELS_DIR, "*.keras")
        keras_files = glob.glob(keras_pattern)
        user_ids = [
            os.path.splitext(os.path.basename(filename))[0] for filename in keras_files
        ]
        _logger.info("Found %d users with trained models: %s", len(user_ids), user_ids)
        return user_ids
    except (IOError, OSError) as e:
        _logger.error("Error getting user IDs: %s", e)
        return []


def populate_user_data(user_id: str) -> dict | None:
    """
    Populate lists for a user, using cache when available
    Returns: A dictionary containing user data, or None if data cannot be populated.
    """
    cached_data = get_user_data_cache(user_id)
    if cached_data:
        return cached_data

    movie_ids, ratings = get_movie_ratings(user_id)
    unique_genres = set()
    unique_actors = set()
    unique_directors = set()

    for movie_id in movie_ids:
        movie_details = fetch_movie_details(movie_id)
        if movie_details:
            unique_genres.update(movie_details["genres"])
            unique_actors.update(movie_details["actors"])
            unique_directors.update(movie_details["director"])

    genre_list = sorted(list(unique_genres))
    actor_list = sorted(list(unique_actors))
    director_list = sorted(list(unique_directors))
    num_movies = len(movie_ids)

    set_user_data_cache(
        user_id, genre_list, actor_list, director_list, num_movies, movie_ids, ratings
    )

    return {
        "genre_list": genre_list,
        "actor_list": actor_list,
        "director_list": director_list,
        "num_movies": num_movies,
        "movie_ids": movie_ids,
        "ratings": ratings,
    }


def compute_user_suggestions(user_id: str) -> list:
    """Compute suggestions for a specific user"""
    try:
        _logger.info("Computing suggestions for user: %s", user_id)

        try:
            model_path = get_model_path(user_id)
            user_model = load_model(model_path)
            model_metadata = load_model_metadata(user_id)
            if not model_metadata:
                _logger.error(
                    "Metadata not found for user %s, cannot compute suggestions.",
                    user_id,
                )
                return []
        except (IOError, OSError, ImportError) as e:
            _logger.error(
                "Failed to load model or metadata for user %s: %s", user_id, e
            )
            return []

        user_genre_list = model_metadata["genre_list"]
        user_actor_list = model_metadata["actor_list"]
        user_director_list = model_metadata["director_list"]
        user_num_movies = model_metadata["num_movies"]

        releases_1 = fetch_new_releases(1) or []
        releases_2 = fetch_new_releases(2) or []
        new_releases = releases_1 + releases_2
        watchlist_movie_ids = get_movie_ids(user_id)

        filtered_movies = [
            movie for movie in new_releases if movie["id"] not in watchlist_movie_ids
        ]

        filtered_movies = [movie for movie in filtered_movies if movie["score"] >= 7.0]

        if not filtered_movies:
            return []

        def fetch_and_preprocess_movie(movie):
            try:
                movie_details = fetch_movie_details(movie["id"])
                if movie_details:
                    movie_data = preprocess_movie_data(
                        movie_details,
                        user_genre_list,
                        user_actor_list,
                        user_director_list,
                    )
                    return movie, movie_data
            except (KeyError, ValueError, TypeError) as e:
                _logger.error("Error processing movie %s: %s", movie.get("id"), e)
            return None

        processed_movies = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_movie = {
                executor.submit(fetch_and_preprocess_movie, movie): movie
                for movie in filtered_movies
            }

            for future in as_completed(future_to_movie):
                result = future.result()
                if result:
                    processed_movies.append(result)

        if not processed_movies:
            return []

        batch_size = len(processed_movies)

        user_ids = np.zeros(batch_size, dtype=np.int32)
        movie_indices = np.full(batch_size, user_num_movies, dtype=np.int32)
        genre_vectors = np.zeros((batch_size, len(user_genre_list)), dtype=np.float32)
        release_years = np.zeros((batch_size, 1), dtype=np.float32)
        durations = np.zeros((batch_size, 1), dtype=np.float32)
        popularities = np.zeros((batch_size, 1), dtype=np.float32)
        actor_vectors = np.zeros((batch_size, len(user_actor_list)), dtype=np.float32)
        director_vectors = np.zeros(
            (batch_size, len(user_director_list)), dtype=np.float32
        )
        average_ratings = np.zeros((batch_size, 1), dtype=np.float32)

        movies_list = []
        for i, (movie, movie_data) in enumerate(processed_movies):
            movies_list.append(movie)
            user_ids[i] = 0
            genre_vectors[i] = movie_data["genre_vector"]
            release_years[i, 0] = movie_data["release_year"]
            durations[i, 0] = movie_data["duration"]
            popularities[i, 0] = movie_data["popularity"]
            actor_vectors[i] = movie_data["actor_vector"]
            director_vectors[i] = movie_data["director_vector"]
            average_ratings[i, 0] = movie_data["average_rating"]

        try:
            batch_predictions = user_model.predict(
                [
                    user_ids,
                    movie_indices,
                    genre_vectors,
                    release_years,
                    durations,
                    popularities,
                    actor_vectors,
                    director_vectors,
                    average_ratings,
                ],
                batch_size=batch_size,
            )

            for i, movie in enumerate(movies_list):
                movie["predicted_rating"] = float(batch_predictions[i][0] * 5)

        except (ValueError, RuntimeError, IndexError) as e:
            _logger.error("Error during batch prediction for user %s: %s", user_id, e)
            return []

        sorted_movies = sorted(
            movies_list, key=lambda x: x["predicted_rating"], reverse=True
        )

        _logger.info(
            "Computed %d suggestions for user: %s", len(sorted_movies), user_id
        )
        return sorted_movies

    except (IOError, OSError, KeyError, ValueError) as e:
        _logger.error("Error computing suggestions for user %s: %s", user_id, e)
        return []


def update_all_user_suggestions():
    """Update suggestions cache for all users"""
    _logger.info("Starting scheduled update of all user suggestions")
    start_time = time.time()

    user_ids = get_all_user_ids()
    total_users = len(user_ids)

    if total_users == 0:
        _logger.info("No users found with trained models")
        return

    successful_updates = 0

    for i, user_id in enumerate(user_ids, 1):
        try:
            _logger.info(
                "Updating suggestions for user %s (%d/%d)", user_id, i, total_users
            )
            suggestions = compute_user_suggestions(user_id)
            set_suggestions_cache(user_id, suggestions)
            successful_updates += 1
        except (IOError, OSError, ValueError) as e:
            _logger.error("Failed to update suggestions for user %s: %s", user_id, e)

    end_time = time.time()
    duration = end_time - start_time

    _logger.info(
        "Scheduled update completed: %d/%d users updated in %.2f seconds",
        successful_updates,
        total_users,
        duration,
    )


def training_worker():
    """Worker function that processes training requests sequentially"""
    while True:
        try:
            user_id = training_queue.get(timeout=60)
            if user_id is None:
                break
            _execute_training(user_id)
            training_queue.task_done()
        except queue.Empty:
            continue
        except (IOError, OSError, ValueError, RuntimeError) as e:
            _logger.error("Training worker error: %s", e)
            training_queue.task_done()


def _execute_training(user_id: str):
    """Execute the actual training process"""
    try:
        _logger.info("Starting training for user: %s", user_id)

        invalidate_caches(user_id)

        user_data = populate_user_data(user_id)
        if not user_data:
            _logger.error(
                "Could not populate user data for %s. Aborting training.", user_id
            )
            return

        new_model = build_model(
            num_movies=user_data["num_movies"] + 1,
            num_genres=len(user_data["genre_list"]),
            num_actors=len(user_data["actor_list"]),
            num_directors=len(user_data["director_list"]),
        )

        new_model = train_model(
            new_model,
            user_data["movie_ids"],
            user_data["ratings"],
            user_data["genre_list"],
            user_data["actor_list"],
            user_data["director_list"],
        )
        model_path = get_model_path(user_id)
        new_model.save(model_path)

        metadata = {
            "genre_list": user_data["genre_list"],
            "actor_list": user_data["actor_list"],
            "director_list": user_data["director_list"],
            "num_movies": user_data["num_movies"],
        }
        save_model_metadata(user_id, metadata)

        _logger.info("Training completed successfully for user: %s", user_id)

        try:
            _logger.info("Computing suggestions after training for user: %s", user_id)
            suggestions = compute_user_suggestions(user_id)
            set_suggestions_cache(user_id, suggestions)
        except (IOError, OSError, ValueError, RuntimeError) as e:
            _logger.error(
                "Error computing suggestions after training for user %s: %s", user_id, e
            )

    except (IOError, OSError, ValueError, RuntimeError) as e:
        _logger.error("Error during training for user %s: %s", user_id, e)


def process_training_request(user_id: str):
    """Process a training request by queuing it for training"""
    try:
        _logger.info("Queuing training request for user: %s", user_id)

        invalidate_caches(user_id)

        training_queue.put(user_id)

    except (IOError, OSError, ValueError, RuntimeError) as e:
        _logger.error("Error processing training request: %s", e)


def _run_scheduler():
    """Run the schedule loop in a background thread, checking every minute."""
    scheduled_time = os.getenv("RETRAIN_SCHEDULE_TIME", "02:00")
    schedule.every().day.at(scheduled_time).do(update_all_user_suggestions)
    _logger.info(
        "Scheduler started: update_all_user_suggestions scheduled daily at %s",
        scheduled_time,
    )

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except (RuntimeError, ValueError) as e:
            _logger.error("Scheduler error: %s", e)


def start_background_threads():
    """Start the training worker and daily scheduler as daemon threads,
    then run an initial suggestions update for all users."""
    training_thread = threading.Thread(target=training_worker, daemon=True)
    scheduler_thread = threading.Thread(target=_run_scheduler, daemon=True)

    training_thread.start()
    scheduler_thread.start()

    _logger.info("Background threads started: training_worker & scheduler")

    # Run an initial suggestions update on startup
    _logger.info("Running initial suggestions update on startup")
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(update_all_user_suggestions)
