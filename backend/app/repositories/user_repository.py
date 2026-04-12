import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User

class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._db.scalars(stmt).first()

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._db.get(User, user_id)