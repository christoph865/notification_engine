import pytest
from fastapi import status
from httpx import AsyncClient

# All test functions using async/await syntax must carry this marker token in Pytest 8+
pytestmark = pytest.mark.asyncio


async def test_root_health_check(async_client: AsyncClient):
    """
    Garantierte Verifizierung unseres globalen Healthchecks.
    Erwartet ein sauberes JSON-Objekt und den HTTP-Status 200 OK.
    """
    # 1. Fire a mock GET request directly into our memory event loop
    response = await async_client.get("/")

    # 2. Execute strict assertions to validate response state integrity
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "project" in data


async def test_send_notification_validation_firewall_blocks_invalid_payload(async_client: AsyncClient):
    """
    Beweist, dass unsere Pydantic-Validierung fehlerhafte Payloads (z. B. ungültige Typen)
    erfolgreich blockiert, bevor sie die Datenbank oder den Worker kontaktiert.
    """
    # 1. Structure an invalid payload (e.g., passing 'fax' which is not in our NotificationType Enum)
    invalid_payload = {
        "type": "fax",
        "recipient": "test@market.com",
        "title": "Broken Intentions",
        "content": "This will crash the front door firewall rules."
    }

    # 2. Fire the post request
    response = await async_client.post("/api/v1/send", json=invalid_payload)

    # 3. Expect an automated '422 Unprocessable Content' rejection from Pydantic
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_send_notification_accepts_and_queues_valid_payload(async_client: AsyncClient):
    """
    Verifiziert den optimalen 'Happy Path'. 
    Ein valider Request muss sofort mit HTTP 202 Accepted und dem Status 'queued' antworten.
    """
    valid_payload = {
        "type": "email",
        "recipient": "developer@testcompany.com",
        "title": "Automated Testing Verification",
        "content": "Pytest execution engine validation is functional."
    }

    response = await async_client.post("/api/v1/send", json=valid_payload)

    # Expect our modern asynchronous 202 Accepted hand-off token code
    assert response.status_code == status.HTTP_202_ACCEPTED
    
    data = response.json()
    assert data["status"] == "queued"
    assert "task_id" in data
