# Notification Engine

Asynchronous notification delivery system built with **FastAPI**, **Celery**, and **Redis**. Fast API responses (<20ms) with reliable background processing and automatic retry logic.

## Features

- Asynchronous notification delivery via Celery/Redis
- FastAPI with automatic API documentation (Swagger UI)
- Database transaction logging with status tracking
- Automatic retry & crash recovery
- Type-safe with Pydantic validation

## Tech Stack

- FastAPI 0.141.1 | Uvicorn 0.52.4
- Celery + Redis (message broker)
- SQLAlchemy + Pydantic
- Python 3.8+

## Quick Start

### Prerequisites
- Python 3.8+
- Docker (for Redis)

### Installation

```bash
# Clone and setup
git clone <repository-url>
cd notification-engine
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running

```bash
# Start Redis
docker run -d -p 6379:6379 redis:latest

# Start FastAPI server
uvicorn src.main:app --reload

# Start Celery worker (in another terminal)
celery -A src.tasks.send_task worker --loglevel=info
```

API available at `http://localhost:8000`
Docs at `http://localhost:8000/docs`

## Usage Example

```bash
curl -X POST http://localhost:8000/api/v1/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "user@example.com",
    "subject": "Test",
    "message": "Hello!"
  }'
```

Response: HTTP 202 Accepted with notification ID

## Environment Variables

```env
PROJECT_NAME=Notification Engine
API_V1_STR=/api/v1
DATABASE_URL=sqlite:///./notification.db
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
```

## Architecture

- **Request Phase**: FastAPI validates payload, logs to DB (PENDING), enqueues task, returns 202
- **Background Phase**: Celery worker processes notification asynchronously
- **Crash Recovery**: Failed tasks automatically retry with rollback/re-queue

## License

MIT
