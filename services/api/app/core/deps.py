from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.repositories.user_repository import UserRepository

# HTTPBearer tells FastAPI + Swagger: "this endpoint needs an Authorization: Bearer <token> header"
security = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(creds.credentials, settings.jwt_secret,
                             algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":            # reject refresh tokens here
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong token type")
        user_id = payload["sub"]
    except JWTError:                                    # expired, tampered, or malformed
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User no longer exists")
    return user