# FastAPI URL Shortener

A high-performance URL shortener service built with FastAPI. Features a pre-allocated code pool system with reservation-based allocation to minimize collisions and race conditions.

## Features

- **Fast URL shortening**: Convert long URLs to 5-character short codes
- **Efficient allocation**: Pre-generated code pool with reservation mechanism to avoid collisions
- **Flexible storage**: SQLite (development) or PostgreSQL (production)
- **Async task queue**: Celery workers for background code pool seeding
- **Scheduled maintenance**: Celery Beat for releasing stale reserved codes
- **Centralized configuration**: Environment-based settings management with Pydantic
- **Full test coverage**: Comprehensive pytest test suite with fixtures

## Architecture

### Code Pool System
The system maintains a pool of pre-generated short codes to minimize collisions and race conditions:

1. **Code Pool Generation**: Celery Beat runs hourly to seed the code pool, generating available codes
2. **Code Reservation**: When shortening a URL, a code is reserved (marked as `reserved` status)
3. **Code Activation**: After successful URL storage, the code is marked as `used`
4. **Stale Code Release**: Celery Beat releases reserved codes that haven't been completed within a timeout (default 5 minutes)

### Service Components
- **FastAPI App**: HTTP API for URL shortening and redirection
- **PostgreSQL/SQLite**: Persistent storage for URLs and code pool
- **Redis**: Message broker for Celery task queue
- **Celery Worker**: Processes async tasks (code pool seeding)
- **Celery Beat**: Scheduler for periodic tasks

## Quick Start

### Local Development (SQLite)

```bash
# Clone and setup
git clone <repo>
cd shortener

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy example config
cp .env.example .env

# Run migrations (if needed)
# python -m alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

The app will be available at `http://localhost:8000`

### Docker Setup (PostgreSQL + Redis + Celery)

```bash
# Copy Docker environment file
cp .env.docker.example .env.docker  # if needed

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

The app will be available at `http://localhost:8000`

Database will persist in the `postgres_data` volume.

## Configuration

Configuration is centralized in `app/config.py` and loaded from environment variables via `.env` file.

### Database Configuration

Choose between SQLite (development) or PostgreSQL (production):

```env
# Development (SQLite)
DATABASE_TYPE=sqlite
SQLITE_PATH=./shortener.db

# Production (PostgreSQL)
DATABASE_TYPE=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=shortener
```

### Code Pool Configuration

```env
CODE_POOL_TARGET_AVAILABLE=1000     # Target number of available codes in pool
RESERVED_CODE_TIMEOUT_SECONDS=300   # Max seconds to hold a reservation
```

### Celery & Redis Configuration

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

For Docker, use container service names:
```env
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Database Migrations

This project uses **Alembic** for database schema versioning and migration management. Migrations are automatically executed at deployment time before the application starts.

### How Migrations Work

1. **Automatic Execution on Docker Deploy**: The `docker-compose.yml` includes a dedicated `migrations` service that runs `alembic upgrade head` before the app starts. This ensures schema changes are applied in order and without manual intervention.

2. **Migration Files**: All migrations are stored in `alembic/versions/` directory with naming convention: `{revision_id}_{description}.py`

3. **Initial Schema**: The initial migration (`33b713a717d4_initial_migration.py`) creates two tables:
   - `url_map`: Stores URL mappings (code → long_url)
   - `code_pool`: Manages short code lifecycle and reservation states

### Creating a New Migration

When you modify SQLAlchemy models in `app/models.py`:

```bash
# Auto-generate migration (detects model changes)
alembic revision --autogenerate -m "description of changes"

# Review the generated migration file in alembic/versions/
# Edit if needed to ensure correctness

# Apply migration locally
alembic upgrade head
```

### Applying Migrations Locally

```bash
# Apply all pending migrations
alembic upgrade head

# Revert last migration (if needed)
alembic downgrade -1

# View migration history
alembic history

# Check current version
alembic current
```

### Deployment Flow

When you run `docker-compose up`:

1. **Database starts** → health check verifies PostgreSQL is ready
2. **Migrations run** → `migrations` service executes `alembic upgrade head` and exits
3. **App starts** → `app` service waits for migrations to complete, then starts FastAPI
4. **Workers start** → Celery worker and beat services start after DB is healthy

This order is enforced by the `depends_on` configuration with health checks and `service_completed_successfully` conditions.

### Important Notes

- Migrations are **idempotent** — running them multiple times is safe
- Always review auto-generated migrations before committing
- Migration failures will prevent the app from starting (by design — prevents partial deployments)
- Each migration is versioned and tracked in the `alembic_version` table

## API Endpoints

### Shorten a URL
```http
POST /shorten
Content-Type: application/json

{
  "url": "https://example.com/very/long/path"
}
```

Response:
```json
{
  "code": "abc12",
  "short_url": "http://localhost:8000/abc12"
}
```

### Redirect to Original URL
```http
GET /{code}
```

Redirects to the original URL if the code exists. Returns 404 if not found.

## Testing

Run the full test suite:

```bash
pytest
```

Run specific test:

```bash
pytest tests/test_main.py::test_shorten_url_returns_code -v
```

## Project Structure

```
.
├── app/
│   ├── main.py           # FastAPI application and routes
│   ├── config.py         # Configuration management (Pydantic Settings)
│   ├── database.py       # Database connection and session management
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── repository.py     # Data access layer
│   ├── celery_app.py     # Celery configuration and beat schedule
│   ├── tasks.py          # Celery task definitions
│   └── errors.py         # Custom exception classes
├── tests/
│   └── test_main.py      # Test suite
├── docker-compose.yml    # Docker services definition
├── Dockerfile            # Docker image build config
├── .env.example          # Example environment variables
├── .env.docker           # Docker-specific environment variables
└── README.md             # This file
```

## Design Decisions

1. **Code Pool Strategy**: Pre-generated codes with reservation reduces collision probability and improves performance compared to on-the-fly generation.

2. **SQLite + PostgreSQL Support**: SQLite for development simplicity, PostgreSQL for production reliability. Switch via environment variable.

3. **Celery Background Tasks**: Separates code pool maintenance from HTTP request handling, allowing independent scaling.

4. **Deterministic Code Generation**: Codes are generated deterministically from URLs, making the system idempotent.

5. **No Delete Flow**: URL records are permanent. Codes can only transition: `available` → `reserved` → `used`.

## Performance Considerations

- **Code Pool Pre-allocation**: Reduces blocking I/O during shortening requests
- **Health Checks**: Docker services include health checks for reliability
- **Connection Pooling**: SQLAlchemy pool settings optimized for SQLite and PostgreSQL
- **Reserved Code Cleanup**: Periodic cleanup prevents pool exhaustion from incomplete reservations

## Future Improvements

- Add caching layer (Redis) for redirects
- Implement custom code support
- Add click analytics tracking
- Database indexing optimization for large datasets
- Read replicas for scaling read-heavy workloads
- API rate limiting
