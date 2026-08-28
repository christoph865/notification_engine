from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# All these absolute imports will now resolve perfectly!
from src.api.deps import get_db
from src.db.models.notification import Notification
from src.schemas.notification import NotificationCreate

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

@router.post("/send", status_code=status.HTTP_201_CREATED)
def send_notification(payload: NotificationCreate, db: Session = Depends(get_db)):
    """
    Ingest a new notification request, validate its structure,
    and persist it securely into the historical relational tracking log.
    """
    try:
        # 1. Instantiate our database model using the validated payload inputs
        new_notification = Notification(
            type=payload.type,
            recipient=payload.recipient,
            title=payload.title,
            content=payload.content
        )
        
        # 2. Stage the row inside the active database transaction session pool
        db.add(new_notification)
        
        # 3. Permanently write and commit the transaction into the database file
        db.commit()
        
        # 4. Refresh our Python instance to read back the auto-generated UUID and audit logs
        db.refresh(new_notification)
        
        return {
            "status": "persisted",
            "message": "Notification record created successfully.",
            "record": {
                "id": new_notification.id,
                "type": new_notification.type,
                "recipient": new_notification.recipient,
                "status": new_notification.status,
                "created_at": new_notification.created_at
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion failed: {str(e)}"
        )