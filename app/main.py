from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.database import init_db
from app.dependencies import get_url_repository
from app.repositories.interfaces import URLRepository
from app.schemas import ShortenRequest, ShortenResponse
from app.service import make_code

app = FastAPI(title="URL Shortener", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(
    payload: ShortenRequest,
    request: Request,
    repository: URLRepository = Depends(get_url_repository),
):
    long_url = str(payload.url)

    existing = repository.get_by_long_url(long_url)
    if existing:
        return ShortenResponse(
            short_url=str(request.base_url) + existing.code,
            code=existing.code,
            original_url=existing.long_url,
        )

    for attempt in range(20):
        code = make_code(long_url, attempt=attempt)
        taken = repository.get_by_code(code)
        if not taken:
            record = repository.create(code=code, long_url=long_url)
            return ShortenResponse(
                short_url=str(request.base_url) + record.code,
                code=record.code,
                original_url=record.long_url,
            )

    raise HTTPException(status_code=503, detail="Unable to allocate short code")


@app.get("/{code}")
def redirect_short_url(code: str, repository: URLRepository = Depends(get_url_repository)):
    if len(code) > 5:
        raise HTTPException(status_code=404, detail="Not found")

    record = repository.get_by_code(code)
    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=record.long_url, status_code=307)
