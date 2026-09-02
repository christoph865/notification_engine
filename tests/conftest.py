import pytest
from typing import AsyncGenerator, Generator
import httpx
from httpx import AsyncClient, ASGITransport  # ◄── FIX: Cleaned and updated imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.api.deps import get_db
from src.core.database import Base

# 1. Initialize an ultra-fast, isolated in-memory SQLite database engine for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, # StaticPool holds the connection open in memory across threads
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    """
    Automated fixture that creates database schemas before each single test 
    function executes and completely wipes/drops them after completion.
    """
    # Setup step: Construct tables cleanly in-memory
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown step: Drop everything to guarantee full state isolation
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session() -> Generator[TestingSessionLocal, None, None]:  # type: ignore
    """
    Yields an isolated transactional testing session pool block.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """
    Provisions a high-performance HTTPX AsyncClient context wrapper, 
    overriding FastAPI's active production database dependency injector tokens.
    """
    def _override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    # Inject our testing session override straight into the FastAPI application instance
    app.dependency_overrides[get_db] = _override_get_db
    
    # Yield the async client mapped to the ASGI app layout architecture context
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client
        
    # Teardown step: Clear overrides to prevent polluting external scope configurations
    app.dependency_overrides.clear()
