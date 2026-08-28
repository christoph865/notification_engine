from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application Settings Manager using Pydantic.
    Loads and validates environment variables automatically.
    """
    PROJECT_NAME: str = "Notification Engine"
    API_V1_STR: str = "/api/v1"
    
    # ◄── HIER: Diese Zeile hat gefehlt! Das ist der Pfad zu deiner lokalen SQLite-Datenbank.
    DATABASE_URL: str = "sqlite:///./local_development.db"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()



