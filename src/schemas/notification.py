from pydantic import BaseModel, Field
from enum import Enum

class NotificationType(str, Enum):
    """Supported channels allowed by our task orchestration engine."""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"

class NotificationCreate(BaseModel):
    """Schema to validate incoming requests to trigger a background notification."""
    type: NotificationType
    recipient: str = Field(..., description="The target email address, phone number, or webhook URL destination")
    title: str = Field(..., min_length=3, max_length=100, description="The subject or header label of the notification")
    content: str = Field(..., min_length=1, description="The main text payload of the message body")



