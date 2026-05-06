# FastAPI URL Shortener

A simple URL shortener service built with FastAPI.

## Features
- Shorten long URLs into 5-character codes
- Redirect short URLs to the original long URL
- Persistent storage with SQLite + SQLAlchemy
- Input validation and error handling
- Basic performance-minded design (indexed lookups, deterministic keys with collision handling)

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API
### Create short URL
`POST /shorten`

Request:
```json
{
  "url": "https://example.com/some/very/long/path"
}
```

Response:
```json
{
  "short_code": "a1B2c",
  "short_url": "http://localhost:8000/a1B2c",
  "original_url": "https://example.com/some/very/long/path"
}
```

### Redirect
`GET /{short_code}`

Returns HTTP 307 redirect to original URL.

## Test
```bash
pytest -q
```
