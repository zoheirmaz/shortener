# FastAPI URL Shortener

A simple URL shortener service built with FastAPI.

## Features

- Convert long URLs to short codes (max 5 characters)
- Redirect short URLs to original URLs
- Persistent storage with PostgreSQL (Docker) / SQLite (local default) + SQLAlchemy
- Deterministic code generation with collision handling
- Test coverage with pytest

## Suggested dependencies

- **fastapi**: API framework
- **uvicorn[standard]**: ASGI server
- **sqlalchemy**: persistence layer
- **psycopg[binary]**: PostgreSQL driver
- **pydantic**: validation
- **pytest** and **httpx**: testing
- **ruff**: linting

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Endpoints

- `POST /shorten`
  - body: `{ "url": "https://example.com" }`
- `GET /{code}`
  - redirects to original URL if found

## Design notes

- URL records are stored permanently (no delete/update flow).
- Short code length is capped at 5.
- SHA-256 + base62 is used for deterministic generation, with retry attempts for collisions.
- Docker Compose runs PostgreSQL by default. Local runs fall back to SQLite unless `DATABASE_URL` is set.
- For larger scale, add caching (e.g., Redis), proper indexing, and read replicas.
