# Notification Engine

A high-performance, asynchronous notification delivery system built with **FastAPI**, **Celery**, and **Redis**.

## Overview

The Notification Engine is a production-ready notification delivery service that combines synchronous request validation with asynchronous background processing. It uses FastAPI for rapid request handling, Celery for distributed task processing, and Redis for message queuing. The system guarantees fast API responses (< 20ms) while reliably handling notification delivery in the background with automatic retry logic and crash recovery.

## Architecture Highlights

- **Lightning-Fast API** - Returns HTTP 202 Accepted in milliseconds while processing happens asynchronously
- **Async Task Processing** - Celery workers handle notification delivery independently from the web API
- **Message Queue** - Redis-backed queue ensures reliable task handoff between web and worker layers
- **Graceful Error Handling** - Automatic retry logic with crash recovery for failed notification attempts
- **Database Transaction Logging** - Complete audit trail of notification status (PENDING → PROCESSING → SENT)

## Features

- **Asynchronous Notification Delivery** - Non-blocking API with background task processing
- **FastAPI Framework** - Modern, type-safe web framework with auto-generated OpenAPI docs
- **Celery + Redis** - Distributed task queue for reliable background job processing
- **Database Integration** - SQLAlchemy ORM with automatic table management and status tracking
- **Type Safety** - Full type hints and Pydantic validation on all inputs
- **Configuration Management** - Environment-based settings using Pydantic Settings
- **Retry Logic & Crash Recovery** - Automatic rollback and re-queuing on failures
- **API Versioning** - Organized endpoints under `/api/v1/` for future compatibility
- **Automatic Documentation** - Built-in Swagger UI and ReDoc

## Tech Stack

- **Web Framework**: FastAPI 0.141.1
- **ASGI Server**: Uvicorn 0.52.4
- **Task Queue**: Celery (with Redis broker)
- **Message Broker**: Redis
- **ORM**: SQLAlchemy
- **Validation**: Pydantic 2.13.4
- **Environment Config**: Pydantic Settings + python-dotenv

## Project Structure

```
notification-engine/
├── src/
│   ├── main.py                        # FastAPI application entry point
│   ├── core/
│   │   ├── config.py                  # Configuration settings & environment vars
│   │   └── database.py                # SQLAlchemy engine & session setup
│   ├── api/
│   │   ├── deps.py                    # Request dependencies (DB session injection)
│   │   └── v1/
│   │       └── notifications/         # Notification endpoints & schemas
│   ├── db/
│   │   └── models/
│   │       └── notification.py        # Notification data model with status tracking
│   ├── tasks/
│   │   └── send_task.py              # Celery background worker tasks
│   └── schemas/
│       └── notification.py            # Pydantic validation schemas
├── requirements.txt                   # Python dependencies
└── ablaufplan                         # Workflow architecture diagram
```

## Workflow & Architecture

The system follows a **request-response + background processing** pattern:

### 1. **Request Phase** (Client-facing, <20ms)
   - Client sends HTTP POST to `/api/v1/send` with notification payload
   - Pydantic schema validates the request payload
   - Database session opens and logs initial notification status: `PENDING`
   - Celery task is enqueued to Redis broker
   - API immediately returns HTTP 202 Accepted

### 2. **Background Processing Phase** (Asynchronous)
   - Celery worker polls Redis queue and claims the task
   - Worker updates notification status to `PROCESSING` in database
   - Provider I/O call is executed (simulated 2s latency)
   - On success: status updated to `SENT` and database session closed
   - On failure: automatic retry logic triggered with crash recovery

### 3. **Crash Recovery** (Resilience)
   - Failed tasks trigger rollback of database session
   - Retry counter incremented
   - Task automatically re-queued to Redis via `self.retry()` fallback

## API Endpoints

### Core Notification Endpoint
- `POST /api/v1/send` - Submit notification for asynchronous delivery
  - Request: Notification payload (validated via Pydantic schema)
  - Response: HTTP 202 Accepted with notification ID
  - Processing: Task enqueued to Celery/Redis for background handling

### Status & Monitoring (Future)
- `GET /api/v1/notifications/{id}` - Retrieve notification status
- `GET /api/v1/notifications` - List all notifications with filtering

## Environment Setup

### Prerequisites

- Python 3.8+
- Docker & Docker Compose (for Redis and Celery workers)
- Redis 6.0+
- pip or poetry

### Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd notification-engine
   ```

2. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

### Running the System

#### Start Redis Broker
```bash
docker run -d -p 6379:6379 redis:latest
```

#### Start FastAPI Web Server
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Celery Worker(s)
```bash
celery -A src.tasks.send_task worker --loglevel=info
```

The system is ready when:
- ✅ Web API available at `http://localhost:8000`
- ✅ API docs at `http://localhost:8000/docs` (Swagger)
- ✅ Celery worker connected to Redis broker
- ✅ Redis broker listening on `localhost:6379`

## Database Schema

## Monitoring & Logging

### Celery Logs
Watch Celery worker execution:
```bash
celery -A src.tasks.send_task worker --loglevel=debug
```

### Database Status Tracking
Query notification statuses:
```bash
sqlite3 notification.db "SELECT id, status, retry_count, created_at FROM notification ORDER BY created_at DESC;"
```

### Redis Queue Inspection
Check pending tasks in queue:
```bash
redis-cli LLEN celery  # Queue length
redis-cli KEYS "celery*"  # All Celery keys
```

## Performance Characteristics

- **API Response Time**: < 20ms (HTTP 202 returned before background processing)
- **Background Processing**: ~2-3 seconds (including simulated provider latency)
- **Throughput**: Scales horizontally by adding more Celery workers
- **Reliability**: Guaranteed delivery with automatic retry + crash recovery

## Testing

Run the example notification:
```bash
curl -X POST http://localhost:8000/api/v1/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "user@example.com",
    "subject": "Test Notification",
    "message": "This is a test"
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "created_at": "2026-08-29T10:30:00Z"
}
```

Then query the status:
```bash
curl http://localhost:8000/api/v1/notifications/550e8400-e29b-41d4-a716-446655440000
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ConnectionError: Failed to connect to Redis` | Start Redis: `docker run -d -p 6379:6379 redis:latest` |
| `Celery worker not processing tasks` | Check worker is running and connected to broker |
| `HTTP 422 Validation Error` | Verify JSON payload matches Pydantic schema |
| `Database locked` | Ensure only one worker is writing to SQLite (use PostgreSQL for production) |

## Production Deployment

For production deployments, consider:

- **Database**: Switch from SQLite to PostgreSQL or MySQL for concurrent access
- **Message Broker**: Use managed Redis (AWS ElastiCache, Redis Cloud, etc.)
- **Worker Scaling**: Deploy multiple Celery workers behind load balancer
- **Monitoring**: Integrate Flower (Celery monitoring) or Prometheus
- **Logging**: Centralize logs via ELK Stack or similar
- **Container Orchestration**: Deploy with Docker Compose or Kubernetes

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
