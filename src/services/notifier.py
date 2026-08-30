import hmac
import hashlib
import json
import logging
from datetime import datetime, timezone
import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)

class NotificationDispatcher:
    """
    Domain Service Layer responsible for routing and dispatching notification 
    payloads to external networks and third-party APIs.
    """

    @staticmethod
    def sign_payload(payload_bytes: bytes, secret_key: str) -> str:
        """
        Generates a secure HMAC-SHA256 signature to protect the webhook payload 
        from tampering and malicious injection vulnerabilities.
        """
        return hmac.new(
            key=secret_key.encode("utf-8"),
            msg=payload_bytes,
            digestmod=hashlib.sha256
        ).hexdigest()

    @classmethod
    def dispatch_webhook(cls, destination_url: str, title: str, content: str) -> bool:
        """
        Executes a secure, signed outbound HTTP POST request to an external server.
        """
        # 1. Structure the exact event data layout
        webhook_data = {
            "event": "notification.delivered",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "title": title,
                "content": content
            }
        }
        
        # 2. Serialize the dictionary to exact, compact JSON byte formatting
        payload_bytes = json.dumps(webhook_data, separators=(",", ":")).encode("utf-8")
        
        # 3. Calculate the cryptographic security signature hash code
        signature = cls.sign_payload(payload_bytes, settings.WEBHOOK_SECRET_KEY)
        
        # 4. Attach standard enterprise metadata tracking headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "NotificationEngine/2026.1.0",
            "X-Webhook-Signature": signature,  # ◄── The Security Token Proof Header!
            "X-Timestamp": str(int(datetime.now(timezone.utc).timestamp()))
        }
        
        # 5. Spin up a synchronous HTTP client context block to dispatch the request
        try:
            logger.info(f"Sending signed webhook payload to endpoint: {destination_url}")
            with httpx.Client(timeout=10.0) as client:
                response = client.post(destination_url, content=payload_bytes, headers=headers)
                
                # Check if the external server responded with a healthy 2xx status code
                response.raise_for_status()
                logger.info(f"Webhook delivery acknowledged successfully by remote target. Status: {response.status_code}")
                return True
                
        except httpx.HTTPStatusError as err:
            logger.error(f"External webhook server rejected dispatch with error status: {err.response.status_code}")
            raise err
        except Exception as err:
            logger.error(f"Network transport level connection timeout or failure: {str(err)}")
            raise err
