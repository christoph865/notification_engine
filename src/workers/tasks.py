import time
import logging
from celery.utils.log import get_task_logger
from src.core.cel_app import celery_app
from src.core.database import SessionLocal
from src.db.models.notification import Notification, NotificationStatus

# 1. Initialize a specialized Celery worker thread-safe logger
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
    simulates external API networking, and updates its execution status.
    """
    logger.info(f"Starting execution for Notification ID: {notification_id}")
    
    # 2. Open an isolated request-scoped database context session pipeline
    db = SessionLocal()
    
    try:
        # 3. Retrieve the matching notification row from the database
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        
        if not notification:
            logger.error(f"Notification {notification_id} not found in database records.")
            return f"Error: Notification {notification_id} not found."
            
        # 4. Advance status from PENDING to PROCESSING
        notification.status = NotificationStatus.PROCESSING
        db.commit()
        
        # 5. Simulate heavy external network I/O delivery (e.g., hitting SendGrid/Twilio API)
        logger.info(f"Dispatching alert channel: {notification.type} to target: {notification.recipient}")
        time.sleep(2) # ◄── Simulates a 2-second blocking network latency check
        
        # 6. Flag execution as completely successful
        notification.status = NotificationStatus.SENT
        db.commit()
        logger.info(f"Notification {notification_id} successfully sent and logged.")
        return f"Success: Notification {notification_id} sent."
        
    except Exception as exc:
        # If an unexpected network drop happens, safely roll back the database pool
        db.rollback()
        logger.warning(f"Network glitch occurred for task: {notification_id}. Retrying...")
        
        # Increment our analytical database retry tracking counter
        try:
            db_retry = SessionLocal()
            noti = db_retry.query(Notification).filter(Notification.id == notification_id).first()
            if noti:
                noti.retry_count += 1
                db_retry.commit()
        except Exception:
            pass
        finally:
            db_retry.close()
            
        # 7. Automatically re-enqueue the task into Redis with an exponential delay countdown
        raise self.retry(exc=exc)
        
    finally:
        # Guarantee closure of the connection block to prevent execution pool deadlocks
        db.close()