from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.user import UserRepository
from app.services.auth import hash_password
from app.models.user import UserRole


def ensure_initial_user(session: Session) -> None:
    repository = UserRepository(session)
    existing_user = repository.get_by_email(settings.first_superuser_email)
    if existing_user is not None:
        return

    repository.create(
        email=settings.first_superuser_email,
        full_name=settings.first_superuser_name,
        hashed_password=hash_password(settings.first_superuser_password),
        role=UserRole.ADMIN,
    )
