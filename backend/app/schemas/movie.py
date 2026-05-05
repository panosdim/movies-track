from pydantic import BaseModel


class MovieBase(BaseModel):
    title: str
    genre: str
    rating: float
    description: str | None = None


class MovieCreate(MovieBase):
    pass


class Movie(MovieBase):
    id: int

    model_config = {"from_attributes": True}
