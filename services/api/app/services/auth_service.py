from datetime import timedelta
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import create_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, users: UserRepository):
        self.users = users                       # dependency arrives injected, not imported-hard

    def register(self, email: str, password: str) -> None:
        if self.users.get_by_email(email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
        self.users.create(email, hash_password(password))

    def login(self, email: str, password: str) -> tuple[str, str]:
        user = self.users.get_by_email(email)
        # same error for "no user" and "wrong password" — don't leak which emails exist
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        access = create_token(str(user.id),
                              timedelta(minutes=settings.access_token_expire_minutes),
                              "access")
        refresh = create_token(str(user.id),
                               timedelta(days=settings.refresh_token_expire_days),
                               "refresh")
        return access, refresh