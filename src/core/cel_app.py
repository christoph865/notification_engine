from celery import Celery
from src.core.config import settings

# 1. Initialize the central Celery instance
# The first string ist the name of our main package context,
# and broker configures where tasks are queued up.
celery_app = Celery(
    "notification_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL # Stores task performance metadata logs
)

# 2. Enforce market-standard execution rules
celery_app.conf.update(
    task_track_started=True,  # Track when a task starts execution
    task_serializer="json",  # Use JSON for task serialization
    accept_content=["json"],  # Accept only JSON content for tasks
    result_serializer="json",  # Use JSON for result serialization
    timezone="UTC",  # All timestamps are stored in UTC
    enable_utc=True,  # Enforce UTC for all time-related operations
    broker_connection_retry_on_startup=True  # Retry broker connection on startup
)


# 3. Explicitly tell Celery where to look to find background tasks.
celery_app.autodiscover_tasks(["src.workers"])

