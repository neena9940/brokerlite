from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# CryptContext wraps argon2 — if you ever migrate algorithms, old hashes still verify
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)        # argon2: salted + slow by design

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed) # constant-time comparison, no timing leaks

def create_token(subject: str, expires: timedelta, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + expires
    payload = {
        "sub": subject,      # subject = the user's id, as a string
        "exp": expire,       # expiration is INSIDE the token: it can't be forged away
        "type": token_type,  # "access" or "refresh" — prevents swapping one for the other
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)