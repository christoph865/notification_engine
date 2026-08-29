from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application Settings Manager using Pydantic.
    Loads and validates environment variables automatically.
    """
    PROJECT_NAME: str = "Notification Engine"
    API_V1_STR: str = "/api/v1"
    
    # Pfad zu deiner lokalen SQLite-Datenbank.
    DATABASE_URL: str = "sqlite:///./local_development.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()



