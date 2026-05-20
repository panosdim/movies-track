"""Pydantic schemas for movie data validation and serialization."""

from pydantic import BaseModel, Field


class MovieProviderSchema(BaseModel):
    """Schema for streaming provider information."""

    logo_path: str | None = None
    provider_name: str | None = None

    model_config = {"from_attributes": True}


class MovieBase(BaseModel):
    """Base schema for movie data."""

    movie_id: int | None = None
    poster: str | None = None
    rating: int | None = Field(default=None, ge=0, le=5)
    title: str | None = Field(default=None, max_length=255)
    user_id: str | None = None
    watched: bool | None = None


class MovieCreate(MovieBase):
    """Schema for creating a new movie."""


class MovieUpdate(BaseModel):
    """Schema for updating an existing movie."""

    movie_id: int | None = None
    poster: str | None = None
    rating: int | None = Field(default=None, ge=0, le=5)
    title: str | None = Field(default=None, max_length=255)
    user_id: str | None = None
    watched: bool | None = None


class WatchedMovieResponse(BaseModel):
    """Response schema for watched movies."""

    id: int
    movie_id: int | None = None
    poster: str | None = None
    rating: int | None = Field(default=None, ge=0, le=5)
    title: str | None = Field(default=None, max_length=255)

    model_config = {"from_attributes": True}


class WatchlistMovieResponse(BaseModel):
    """Response schema for watchlist movies."""

    id: int
    movie_id: int | None = None
    poster: str | None = None
    title: str | None = Field(default=None, max_length=255)
    providers: list[MovieProviderSchema] = []
    vote_average: float | None = None

    model_config = {"from_attributes": True}


class Movie(MovieBase):
    """Complete movie schema with database ID and provider information."""

    id: int
    providers: list[MovieProviderSchema] = []
    vote_average: float | None = None

    model_config = {"from_attributes": True}
