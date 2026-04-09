from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.core.security import create_access_token
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import Token, UserCreate, UserLogin, UserRead
from app.services.auth import hash_password, verify_password

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, session: Session = Depends(get_db_session)) -> UserRead:
    repository = UserRepository(session)
    existing_user = repository.get_by_email(payload.email)
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = repository.create(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, session: Session = Depends(get_db_session)) -> Token:
    repository = UserRepository(session)
    user = repository.get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return Token(access_token=create_access_token(str(user.id)), user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
