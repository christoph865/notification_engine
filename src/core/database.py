from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.core.config import settings


# 1. Create the engine wrapper that talks directly to the database file.
# 'connect_args' is special rule only needed for local SQLite development.
if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    ) 
else:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)


# 2. Create a sessionmaker factory. Each HTTP request will get its own isolated transaction pipeline.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  


# 3. Create the Base class. Our database models inherit from this to map to real SQL tables. 
Base = declarative_base()