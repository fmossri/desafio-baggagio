import redis

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, redis_dep
from app.core.limiter import LOGIN_RATE_LIMIT, limiter
from app.models.user import User
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse, UserMeResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/login", 
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login",
    response_description="Login efetuado com sucesso"
    )
@limiter.limit(LOGIN_RATE_LIMIT)
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db),
    r: redis.Redis = Depends(redis_dep),
) -> TokenResponse:
    try:
        return AuthService(db, r).login(payload.email, payload.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate",
        )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh",
    response_description="Tokens renovados com sucesso"
)
def refresh(
    payload: RefreshRequest, 
    db: Session = Depends(get_db), 
    r: redis.Redis = Depends(redis_dep)
) -> TokenResponse:
    try:
        return AuthService(db, r).refresh(payload.refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout",
    response_description="Logout efetuado com sucesso"
)
def logout(
    payload: LogoutRequest, 
    db: Session = Depends(get_db), 
    r: redis.Redis = Depends(redis_dep)
) -> None:
    try:
        return AuthService(db,r).logout(access_token=payload.access_token, refresh_plain=payload.refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

@router.get(
    "/me", 
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Me",
    response_description="Informações do usuário autenticado")
def me(user: User = Depends(get_current_user)) -> User:
    return user