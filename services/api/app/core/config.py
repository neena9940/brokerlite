from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # reads from .env automatically; extra="ignore" so a stray env var can't crash the app
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://broker:broker@localhost:5432/brokerlite"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "dev-only-secret-change-me"   # in prod: env var
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15           # short-lived: damage control if stolen
    refresh_token_expire_days: int = 7              # long-lived, but revocable

settings = Settings()   # single instance, imported everywhere