from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.config import settings
from src.core.database import engine, Base
from src.api.v1.notifications import router as notifications_router

# FIX: Ensure this path has 'src.' at the beginning!
from src.db.models.notification import Notification

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup events.
    Ensures database tables exist before the web server accepts traffic.
    """
    Base.metadata.create_all(bind=engine)
    yield
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(
    notifications_router,
    prefix=settings.API_V1_STR,
    tags=["Notifications"]
)

@app.get("/")
def root_health_check():
    return {
        "status": "healthy", 
        "project": settings.PROJECT_NAME
    }