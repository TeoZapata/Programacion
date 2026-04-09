from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(subject: str) -> str:
    expire_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire_at}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, str]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
