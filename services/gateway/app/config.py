from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str = "dev-only-secret-change-me"  # MUST match portfolio service
    jwt_algorithm: str = "HS256"
    redis_url: str = "redis://localhost:6379/0"
    portfolio_url: str = "http://localhost:8002"
    market_url: str = "http://localhost:8001"


settings = Settings()

# The Routing Table: Maps the first URL segment to a backend service
ROUTES = {
    "auth": settings.portfolio_url,
    "portfolio": settings.portfolio_url,
    "orders": settings.portfolio_url,
    "market": settings.market_url,
    "ai": "http://localhost:8003"
}

# Paths that do NOT require a JWT token
PUBLIC_PATHS = {"/auth/register", "/auth/login", "/auth/refresh", "/ai/chat"}
