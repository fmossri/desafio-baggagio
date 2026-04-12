from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._users = UserRepository(db)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self._users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            # Rota deve mapear para 401
            raise ValueError("Invalid Credentials")
        if not user.is_active:
            raise ValueError("User inactive")

        access_token = create_access_token(subject=str(user.id))
        return TokenResponse(access_token=access_token)