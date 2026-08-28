# Notification Engine

A modern, high-performance notification system built with **FastAPI** and **Python**.

## Overview

The Notification Engine is a RESTful API service designed to manage, process, and deliver notifications at scale. Built on top of FastAPI, it provides a robust foundation for handling notification operations with automatic OpenAPI documentation and type safety.

## Features

- **RESTful API** - Clean, intuitive endpoints for notification management
- **FastAPI Framework** - Modern, fast, and production-ready Python web framework
- **Database Integration** - SQLAlchemy ORM with automatic table management
- **Type Safety** - Full type hints and Pydantic validation
- **Configuration Management** - Environment-based settings using Pydantic Settings
- **API Versioning** - Organized API routes under `/api/v1/` for future compatibility
- **Automatic Documentation** - Built-in Swagger UI and ReDoc

## Tech Stack

- **Framework**: FastAPI 0.141.1
- **Server**: Uvicorn 0.52.4
- **ORM**: SQLAlchemy
- **Validation**: Pydantic 2.13.4
- **Environment Config**: Pydantic Settings + python-dotenv

## Project Structure

```
notification-engine/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── database.py      # Database engine and session setup
│   ├── api/
│   │   └── v1/
│   │       └── notifications/  # Notification endpoints
│   └── db/
│       └── models/
│           └── notification.py # Notification data model
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Getting Started

### Prerequisites

- Python 3.8+
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

### Running the Server

Start the development server:

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

**Interactive API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Notifications
- `GET /api/v1/notifications` - Retrieve notifications
- `POST /api/v1/notifications` - Create a new notification
- `GET /api/v1/notifications/{id}` - Get notification by ID
- `PUT /api/v1/notifications/{id}` - Update notification
- `DELETE /api/v1/notifications/{id}` - Delete notification

## Configuration

Configuration is managed through environment variables via Pydantic Settings. Create a `.env` file in the project root:

```env
PROJECT_NAME=Notification Engine
API_V1_STR=/api/v1
DATABASE_URL=sqlite:///./notification.db
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
