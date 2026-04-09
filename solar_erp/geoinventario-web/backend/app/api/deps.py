from collections.abc import Generator, Sequence

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_current_user(
    session: Session = Depends(get_db_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        subject = payload.get("sub")
        user_id = int(subject) if subject is not None else None
    except (ValueError, TypeError):
        raise credentials_exception

    if user_id is None:
        raise credentials_exception

    user = UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


def require_roles(*allowed_roles: UserRole):
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        allowed: Sequence[UserRole] = allowed_roles
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_dependency
