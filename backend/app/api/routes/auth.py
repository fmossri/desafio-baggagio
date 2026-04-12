from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserMeResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/login", 
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login",
    response_description="Login efetuado com sucesso"
    )
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        return AuthService(db).login(payload.email, payload.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate",
        )

@router.get(
    "/me", 
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Me",
    response_description="Informações do usuário autenticado")
def me(user: User = Depends(get_current_user)) -> User:
    return user