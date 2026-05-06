from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError

from app.database import init_db
from app.dependencies import get_url_repository
from app.repositories.interfaces import URLRepository
from app.schemas import ShortenRequest, ShortenResponse
from app.validators import ShortCodeParam

app = FastAPI(title="URL Shortener", version="1.0.0")
CODE_POOL_TARGET_AVAILABLE = 1000


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

    code = repository.allocate_code()
    if not code:
        repository.seed_code_pool(target_available=CODE_POOL_TARGET_AVAILABLE)
        code = repository.allocate_code()

    if not code:
        raise HTTPException(status_code=503, detail="No available short codes")

    try:
        record = repository.create(code=code, long_url=long_url)
    except IntegrityError:
        repository.release_reserved_code(code)
        raise HTTPException(status_code=409, detail="Failed to assign short code")

    return ShortenResponse(
        short_url=str(request.base_url) + record.code,
        code=record.code,
        original_url=record.long_url,
    )


@app.get("/{code}")
def redirect_short_url(
    code: ShortCodeParam,
    repository: URLRepository = Depends(get_url_repository),
):
    record = repository.get_by_code(code)
    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=record.long_url, status_code=307)
