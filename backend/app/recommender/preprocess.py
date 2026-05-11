"""Movie data preprocessing for the recommender model."""


def preprocess_movie_data(
    movie_data: dict,
    genre_list: list[str],
    actor_list: list[str],
    director_list: list[str],
) -> dict:
    """Preprocess raw movie data into normalised feature vectors.

    Args:
        movie_data: Dictionary containing movie details (genres, actors, director, etc.).
        genre_list: Ordered list of all known genres used to build the one-hot vector.
        actor_list: Ordered list of all known actors used to build the one-hot vector.
        director_list: Ordered list of all known directors used to build the one-hot vector.

    Returns:
        Dictionary of normalised feature arrays ready for model input.
    """
    genre_vector = [1 if genre in movie_data["genres"] else 0 for genre in genre_list]
    actor_vector = [1 if actor in movie_data["actors"] else 0 for actor in actor_list]
    director_vector = [
        1 if director in movie_data["director"] else 0 for director in director_list
    ]

    return {
        "genre_vector": genre_vector,
        "release_year": (movie_data["release_year"] - 1900) / 120,
        "duration": movie_data["duration"] / 300,
        "popularity": movie_data["popularity"] / 1000,
        "average_rating": movie_data["average_rating"] / 10,
        "actor_vector": actor_vector,
        "director_vector": director_vector,
    }
