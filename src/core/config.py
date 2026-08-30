from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Settings Manger using Pydantic
    PROJECT_NAME: str = "Notification Engine"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./local_development.db"  # Default to local SQLite for development
    REDIS_URL: str = "redis://localhost:6379/0"  # Default to local Redis for development

    # New Cryptographic Secret Token for signing Webhooks
    WEBHOOK_SECRET_KEY: str = "super-secret-market-standard-signing-token-key-2026"

    model_config = SettingsConfigDict(
        env_file=".env",  # Load environment variables from a .env file if present
        env_file_encoding="utf-8",  # Ensure proper encoding for the .env file
        case_sensitive=True  # Environment variable names are case-sensitive
    )


settings = Settings()

