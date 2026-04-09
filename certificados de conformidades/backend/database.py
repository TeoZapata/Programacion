from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import get_settings


settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.use_sqlite else {},
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def init_db() -> None:
    """Crear todas las tablas en la base de datos."""
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()

