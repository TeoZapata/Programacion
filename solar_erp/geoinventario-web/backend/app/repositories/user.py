from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.session.scalar(statement)

    def get_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)
        return self.session.scalar(statement)

    def create(
        self,
        *,
        email: str,
        full_name: str,
        hashed_password: str,
        role: UserRole = UserRole.OPERATOR,
    ) -> User:
        user = User(email=email, full_name=full_name, hashed_password=hashed_password, role=role)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
