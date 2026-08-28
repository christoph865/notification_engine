from typing import Generator
from src.core.database import SessionLocal

def get_db() -> Generator:
    """
    Dependency injector that opens a clean database session context 
    per HTTP request and ensures it closes automatically after completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()