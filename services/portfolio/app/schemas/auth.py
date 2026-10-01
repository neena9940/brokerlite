from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr          # EmailStr validates the format automatically
    password: str            # min length rules come later (Step 4 hardening)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str