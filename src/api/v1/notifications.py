from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.db.models.notification import Notification
from src.schemas.notification import NotificationCreate
# Import our newly built background task execution function
from src.workers.tasks import send_notification_task

router = APIRouter()

@router.get("/")
def get_notifications_status():
    return {
        "status": "operational", 
        "message": "Notification sub-router initialized successfully."
    }

# ◄── NOTICE: Change status_code to status.HTTP_202_ACCEPTED (Standard for async handoffs)
@router.post("/send", status_code=status.HTTP_202_ACCEPTED)
def send_notification(payload: NotificationCreate, db: Session = Depends(get_db)):
    """
    Ingest a new notification request, validate its structure,
    persist it to the tracking log, and dispatch it asynchronously to Redis.
    """
    try:
        # 1. Stage the initial tracking row inside our database ledger
        new_notification = Notification(
            type=payload.type,
            recipient=payload.recipient,
            title=payload.title,
            content=payload.content
        )
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)
        
        # 2. The Magic Part: Offload the task to the Redis messaging queue
        # .delay() tells Celery to drop the payload information into Redis and return instantly.
        send_notification_task.delay(new_notification.id)
        
        # 3. Instantly respond to the user with a tracking record pointer
        return {
            "status": "queued",
            "message": "Notification successfully queued for background execution.",
            "task_id": new_notification.id,
            "current_state": new_notification.status
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Asynchronous task scheduling failure: {str(e)}"
        )
