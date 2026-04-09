import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import get_settings
from ..deps import get_db
from ..models.user import User
from ..schemas.auth import SessionUser, TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

settings = get_settings()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> tuple[str, str]:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    csrf_token = secrets.token_urlsafe(32)
    to_encode.update({"csrf": csrf_token})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt, csrf_token


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return TokenData(
            user_id=payload.get("user_id"),
            usuario=payload.get("usuario"),
            rol=payload.get("rol"),
            exp=payload.get("exp"),
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from exc


def _get_user_from_token(
    db: Session,
    token: str,
) -> User:
    token_data = decode_token(token)
    if not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin información de usuario",
        )

    user = db.get(User, token_data.user_id)
    if not user or not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> SessionUser:
    user = _get_user_from_token(db, token)
    return SessionUser(
        id=user.id,
        nombre=user.nombre,
        usuario=user.usuario,
        correo=user.correo,
        rol=user.rol,
        activo=user.activo,
        fecha_creacion=user.fecha_creacion,
    )


async def get_current_admin_user(
    current_user: Annotated[SessionUser, Depends(get_current_user)],
) -> SessionUser:
    if current_user.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta operación",
        )
    return current_user


async def csrf_protect(request: Request, token: Annotated[str, Depends(oauth2_scheme)]) -> None:
    """Protección CSRF basada en token incluido en el JWT y enviado en cabecera X-CSRF-Token."""
    if request.method in ("GET", "OPTIONS", "HEAD"):
        return

    header_token = request.headers.get("X-CSRF-Token")
    if not header_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cabecera CSRF faltante",
        )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from exc

    jwt_csrf = payload.get("csrf")
    if not jwt_csrf or not secrets.compare_digest(jwt_csrf, header_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token CSRF inválido",
        )

