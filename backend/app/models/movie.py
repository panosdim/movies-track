from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MovieProvider(Base):
    __tablename__ = "movie_providers"

    # Composite PK not defined in the DDL — use movie_id + provider_name as natural key.
    # SQLAlchemy requires a PK; we declare both columns and use a composite PK.
    movie_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("movie.id"), primary_key=True
    )
    provider_name: Mapped[str] = mapped_column(
        String(255), primary_key=True, nullable=True
    )
    logo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    movie: Mapped["Movie"] = relationship("Movie", back_populates="providers")


class Movie(Base):
    __tablename__ = "movie"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    movie_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    poster: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    watched: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    providers: Mapped[list["MovieProvider"]] = relationship(
        "MovieProvider", back_populates="movie", cascade="all, delete-orphan"
    )
