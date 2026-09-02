# High-Scale Distributed Asynchronous Notification Engine

A production-grade, containerized asynchronous notification orchestration engine built using **FastAPI**, **Redis**, and **Celery**. This architecture implements structural data validation firewalls, request-scoped isolated transaction pipelines backed by a **PostgreSQL** cluster, and secure cryptographic outbound webhook delivery tracking.

## System Architecture Matrix

```text
[ CLIENT TRAFFIC ] ──(localhost:8000)──► [ FastAPI Gateway (api_gateway) ]
                                                    │
                             (Validates inputs via Pydantic Schema Firewalls)
                                                    │
                                                    ▼
                                         [ PostgreSQL Ledger ]
                                      Stamps Row State: "PENDING"
                                                    │
                                        (Offloads Metadata Packet)
                                                    │
                                                    ▼
                                          [ Redis Message Broker ]
                                     (API releases HTTP 202 In <20ms)
                                                    │
                                         (Background Consumer)
                                                    │
                                                    ▼
                                        [ Celery Workers (worker) ]
                                      ├── Advances State: "PROCESSING"
                                      ├── Computes HMAC-SHA256 Signatures
                                      └── Dispatches HTTPX Outbound POST
```

## Deep-Value Tech Stack Specifications
* **Core Application Gateway:** FastAPI running over ASGI Uvicorn workers.
* **In-Memory Message Broker Queue:** Redis 7.2 Cache Loops.
* **Distributed Task Processing Framework:** Celery 5.3 Background Worker Processes.
* **Enterprise Persistence Ledger:** PostgreSQL 16 Cluster Database.
* **Validation & Configurations Sentinel:** Pydantic V2 Framework models (`BaseModel` / `BaseSettings`).
* **Relational ORM Layer Data Mappings:** SQLAlchemy 2.0 type-hinted parameters (`Mapped`).
* **Automated Verification Testing Suite:** Pytest + HTTPX Async Clients running inside RAM.

## Local Infrastructure Command Guide

Ensure you have **Docker Desktop** running on your host machine before triggering execution paths.

### 1. Build and Boot the Multi-Container Stack
Launch the unified orchestration services (FastAPI, Redis, Postgres DB, and Celery background workers simultaneously):
```bash
docker compose up --build
```
Once booted, the interactive Swagger UI panel automatically populates live at: `http://localhost:8000/docs`

### 2. Execute the Automated Testing Suite
Run the isolated in-memory test script cases directly inside the active web application layer space container:
```bash
docker compose exec api_gateway python -m pytest tests/ -v
```

### 3. Tear Down Infrastructure
Stop all containers cleanly and dismantle the virtual internal container network connections:
```bash
docker compose down
```

## Enterprise Cryptographic Webhook Specification
Every outbound payload carrying a medium channel signature type of `"webhook"` computes a mathematical checksum using the **HMAC-SHA256** hash algorithm. The signature code is attached to the secure transport layer via custom request headers to protect receiving targets from malicious data-tampering hazards:
* `X-Webhook-Signature`: Hexadecimal HMAC-SHA256 signature hash code string.
* `X-Timestamp`: Unix boundary tracking timestamp for relay mitigation rules.
