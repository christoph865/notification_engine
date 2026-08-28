from fastapi import APIRouter
from src.schemas.notification import NotificationCreate

# Initialize an isolated router branch for notification endpoints
router = APIRouter()

@router.get("/")
def get_notifications_status():
    """
    Check the operational status of the notification subsystem.
    """
    return {
        "status": "operational", 
        "message": "Notification sub-router initialized successfully."
    }

@router.post("/send")
def send_notification(payload: NotificationCreate):
    """
    Ingest a new notification task, validate its schema constraints, 
    and prepare it for database persistence and execution queues.
    """
    # For now, we echo back the validated payload data to prove our schema works
    return {
        "status": "validated",
        "data_received": payload
    }