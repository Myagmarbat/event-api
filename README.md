# Event API

A FastAPI application for managing events with a PostgreSQL database backend.

## Features

- ✅ CRUD operations for events
- ✅ SQLAlchemy ORM integration
- ✅ Pydantic validation
- ✅ Comprehensive test coverage
- ✅ Docker support

## Installation

### Prerequisites

- Python 3.13+
- PostgreSQL database

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Myagmarbat/event-api.git
cd event-api
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/event_db"
export APP_NAME="event-api"
```

## Running the Application

### Locally

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### Using Docker

```bash
docker build -t event-api .
docker run -e DATABASE_URL="postgresql://..." -p 8000:8080 event-api
```

## API Endpoints

### Health Check
- `GET /health` - Check API health status

### Events
- `POST /events` - Create a new event (returns 201 Created)
- `GET /events` - List all events
- `GET /events/{event_id}` - Get a specific event
- `DELETE /events/{event_id}` - Delete an event (returns 204 No Content)

### Interactive Documentation

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Testing

```bash
pytest tests/
```

## Data Model

### Event

| Field | Type | Description |
|-------|------|-------------|
| id | String(36) | UUID primary key |
| event_type | String(100) | Type of event (indexed) |
| user_id | String(100) | User identifier (indexed) |
| created_at | DateTime | Creation timestamp (indexed) |

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful GET/LIST operations
- `201 Created` - Successful POST operations
- `204 No Content` - Successful DELETE operations
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Environment Variables

- `DATABASE_URL` (required): PostgreSQL connection string
- `APP_NAME` (optional): Application name (default: "event-api")

## Project Structure

```
event-api/
├── app/
│   ├── __init__.py       # Package initialization
│   ├── main.py           # FastAPI application and endpoints
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── db.py             # Database configuration
│   ├── deps.py           # Dependency injection
│   └── config.py         # Application configuration
├── tests/
│   ├── test_events.py    # Integration tests
│   └── test_unit_service.py  # Unit tests (legacy)
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project metadata
└── README.md            # This file
```

## Development

### Code Style

The codebase follows PEP 8 standards with comprehensive docstrings.

### Adding New Endpoints

1. Add models to `app/models.py`
2. Add schemas to `app/schemas.py`
3. Add endpoints to `app/main.py`
4. Add tests to `tests/test_events.py`

## License

MIT
