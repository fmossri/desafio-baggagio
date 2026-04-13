import uuid
import redis
from typing import Any
from collections.abc import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import SessionLocal
from app.models import User
from app.repositories import UserRepository
from app.core.redis_client import get_redis
from app.services.auth_service import deny_jti_key


bearer_scheme = HTTPBearer(auto_error=False)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def redis_dep() -> redis.Redis:
    return get_redis()

def get_current_user(
    db: Session = Depends(get_db),
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    r: redis.Redis = Depends(redis_dep),
) -> User:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload: dict[str, Any] = jwt.decode(
            creds.credentials, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        jti = payload.get("jti")
        if not jti:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        if r.get(deny_jti_key(str(jti))):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        user_id = uuid.UUID(sub)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user
