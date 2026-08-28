import uuid
from enum import Enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base
from src.schemas.notification import NotificationType

class NotificationStatus(str, Enum):
    """Tracks the asynchronous execution lifecycle of a task."""
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"

class Notification(Base):
    """
    SQLAlchemy Model representing the 'notifications' database table.
    Stores historical records of all outbound notifications.
    """
    __tablename__ = "notifications"

    # Primary Key (Using UUID instead of auto-incrementing integers for security)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Core Payload Fields
    type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    
    # System Tracking & Orchestration Fields
    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus), 
        default=NotificationStatus.PENDING, 
        nullable=False
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Automatic Time Audit Logging (Always stored in UTC)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )