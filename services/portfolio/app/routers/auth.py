from datetime import timedelta
from app.core.database import get_db

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, RefreshRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    # the composition root: wire repository -> service here, once
    return AuthService(UserRepository(db))


@router.post("/register", status_code=201)
def register(body: RegisterRequest, auth: AuthService = Depends(get_auth_service)):
    auth.register(body.email, body.password)   # thin: Pydantic validates -> service does the work
    return {"message": "user created"}


@router.post("/login", response_model=TokenResponse)
def login(body: RegisterRequest, auth: AuthService = Depends(get_auth_service)):
    access, refresh = auth.login(body.email, body.password)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh")
def refresh(body: RefreshRequest):
    try:
        payload = jwt.decode(body.refresh_token, settings.jwt_secret,
                             algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Wrong token type")
    except JWTError:
        raise HTTPException(401, "Invalid refresh token")
    access = create_token(payload["sub"],
                          timedelta(minutes=settings.access_token_expire_minutes),
                          "access")
    return {"access_token": access, "token_type": "bearer"}