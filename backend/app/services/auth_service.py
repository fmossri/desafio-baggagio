import secrets
import uuid
import redis
from typing import cast

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.core.auth_ttl import access_deny_ttl_seconds_from_payload, refresh_ttl_seconds


REFRESH_KEY_PREFIX = "refresh:"
DENY_JTI_PREFIX = "deny:jti:"

def refresh_redis_key(opaque: str) -> str:
    return f"{REFRESH_KEY_PREFIX}{opaque}"

def deny_jti_key(jti: str) -> str:
    return f"{DENY_JTI_PREFIX}{jti}"

class AuthService:
    def __init__(self, db: Session, r: redis.Redis) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._r = r

    def login(self, email: str, password: str) -> TokenResponse:
        user = self._users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            # Rota deve mapear para 401
            raise ValueError("Invalid Credentials")
        if not user.is_active:
            raise ValueError("User inactive")

        access_token, _access_jti = create_access_token(subject=str(user.id))
        refresh_plain = secrets.token_urlsafe(32)
        self._r.setex(
            refresh_redis_key(refresh_plain),
            refresh_ttl_seconds(),
            str(user.id),
        )

        return TokenResponse(access_token=access_token, refresh_token=refresh_plain)

    def refresh(self, refresh_plain: str) -> TokenResponse:
        rk = refresh_redis_key(refresh_plain)
        user_id_raw = self._r.get(rk)
        if user_id_raw is None:
            raise ValueError("Invalid refresh token")
        user_id_str = cast(str, user_id_raw)
        if not user_id_str:
            raise ValueError("Invalid refresh token")

        self._r.delete(rk)

        user = self._users.get_by_id(uuid.UUID(user_id_str))
        if not user or not user.is_active:
            raise ValueError("Invalid refresh token")

        access_token, _ = create_access_token(subject=str(user.id))

        new_refresh = secrets.token_urlsafe(32)
        self._r.setex(
            refresh_redis_key(new_refresh),
            refresh_ttl_seconds(),
            str(user.id),
        )

        return TokenResponse(access_token=access_token, refresh_token=new_refresh)

    def logout(self, *, access_token: str, refresh_plain: str | None) -> None:
        try:
            payload = jwt.decode(
                access_token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError:
            raise ValueError("Invalid token")

        if payload.get("type") != "access":
            raise ValueError("Invalid token")

        jti = payload.get("jti")
        if not jti:
            raise ValueError("Invalid token")

        ttl = access_deny_ttl_seconds_from_payload(payload)
        self._r.setex(deny_jti_key(str(jti)), ttl, "1")

        if refresh_plain:
            self._r.delete(refresh_redis_key(refresh_plain))
            