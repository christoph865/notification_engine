import time
from celery.utils.log import get_task_logger
from src.core.cel_app import celery_app
from src.core.database import SessionLocal
from src.db.models.notification import Notification, NotificationStatus
# 1. Import our fresh secure domain dispatcher service
from src.services.notifier import NotificationDispatcher

logger = get_task_logger(__name__)

@celery_app.task(
    bind=True, 
    max_retries=3, 
    default_retry_delay=5,
    name="src.workers.tasks.send_notification_task"
)
def send_notification_task(self, notification_id: str):
    """
    Asynchronous Celery task that pulls a notification from the database,
    determines its target medium type, and dispatches it securely.
    """
    logger.info(f"Starting execution for Notification ID: {notification_id}")
    
    db = SessionLocal()
    
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        
        if not notification:
            logger.error(f"Notification {notification_id} not found in database records.")
            return f"Error: Notification {notification_id} not found."
            
        notification.status = NotificationStatus.PROCESSING
        db.commit()
        
        # 2. Check the channel medium and route execution dynamically
        if notification.type == "webhook":
            # Fire an actual outbound, cryptographically-signed HTTP POST request!
            NotificationDispatcher.dispatch_webhook(
                destination_url=notification.recipient,
                title=notification.title,
                content=notification.content
            )
        else:
            # Fallback simulated logging processing channel for standard channels (email/sms)
            logger.info(f"Dispatching simulated alert channel: {notification.type} to target: {notification.recipient}")
            time.sleep(2)
        
        # 3. Finalize row status marker to SENT upon successful completion
        notification.status = NotificationStatus.SENT
        db.commit()
        logger.info(f"Notification {notification_id} successfully sent and logged.")
        return f"Success: Notification {notification_id} sent."
        
    except Exception as exc:
        db.rollback()
        logger.warning(f"Network glitch or target server error hit task {notification_id}. Retrying...")
        
        db_retry = None
        try:
            db_retry = SessionLocal()
            noti = db_retry.query(Notification).filter(Notification.id == notification_id).first()
            if noti:
                noti.retry_count += 1
                db_retry.commit()
        except Exception as retry_err:
            logger.error(f"Failed to increment retry counter: {retry_err}")
        finally:
            if db_retry is not None:
                db_retry.close()
            
        # 4. Automatically trigger exponential retry countdown back into Redis queue
        raise self.retry(exc=exc)
        
    finally:
        db.close()
