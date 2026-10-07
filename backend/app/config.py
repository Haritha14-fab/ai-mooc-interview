"""Application configuration loaded from the backend environment."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    DATABASE_URL: str = "sqlite:///./ai_mooc.db"
    JWT_SECRET_KEY: str = "development-only-change-before-deploying"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    OPENAI_API_KEY: str | None = None
    CLAUDE_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    CLAUDE_MODEL: str = "claude-sonnet-4-6"
    AI_PROVIDER: str = "openai"
    AI_TIMEOUT_SECONDS: int = 45

    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,testserver"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_secrets(self):
        if self.ENVIRONMENT.lower() == "production":
            insecure_values = {
                "development-only-change-before-deploying",
                "your-secret-key-here-change-in-production",
                "your-jwt-secret-key-here-change-in-production",
            }
            if self.JWT_SECRET_KEY in insecure_values or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("Set a unique JWT_SECRET_KEY of at least 32 characters in production")
            if self.DEBUG:
                raise ValueError("DEBUG must be false in production")
        if self.AI_PROVIDER.lower() not in {"openai", "claude"}:
            raise ValueError("AI_PROVIDER must be either 'openai' or 'claude'")
        if self.ALGORITHM != "HS256":
            raise ValueError("ALGORITHM must be HS256")
        if self.ACCESS_TOKEN_EXPIRE_MINUTES < 1:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
        if self.AI_TIMEOUT_SECONDS < 1:
            raise ValueError("AI_TIMEOUT_SECONDS must be positive")
        if self.ENVIRONMENT.lower() == "production" and (
            "*" in self.ALLOWED_HOSTS or "*" in self.CORS_ORIGINS
        ):
            raise ValueError("Production CORS origins and allowed hosts must be explicit")
        return self


settings = Settings()
