from pydantic import BaseModel, Field


class MovieProviderSchema(BaseModel):
    logo_path: str | None = None
    provider_name: str | None = None

    model_config = {"from_attributes": True}


class MovieBase(BaseModel):
    movie_id: int | None = None
    poster: str | None = None
    rating: int | None = Field(default=None, ge=0, le=5)
    title: str | None = Field(default=None, max_length=255)
    user_id: str | None = None
    watched: bool | None = None


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    movie_id: int | None = None
    poster: str | None = None
    rating: int | None = Field(default=None, ge=0, le=5)
    title: str | None = Field(default=None, max_length=255)
    user_id: str | None = None
    watched: bool | None = None


class Movie(MovieBase):
    id: int
    providers: list[MovieProviderSchema] = []

    model_config = {"from_attributes": True}
