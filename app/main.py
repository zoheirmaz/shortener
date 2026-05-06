from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.models import URLMap
from app.schemas import ShortenRequest, ShortenResponse
from app.service import make_code

app = FastAPI(title="URL Shortener", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(payload: ShortenRequest, request: Request, db: Session = Depends(get_db)):
    long_url = str(payload.url)

    existing = db.scalar(select(URLMap).where(URLMap.long_url == long_url))
    if existing:
        return ShortenResponse(
            short_url=str(request.base_url) + existing.code,
            code=existing.code,
            original_url=existing.long_url,
        )

    for attempt in range(20):
        code = make_code(long_url, attempt=attempt)
        taken = db.scalar(select(URLMap).where(URLMap.code == code))
        if not taken:
            record = URLMap(code=code, long_url=long_url)
            db.add(record)
            db.commit()
            return ShortenResponse(
                short_url=str(request.base_url) + code,
                code=code,
                original_url=long_url,
            )

    raise HTTPException(status_code=503, detail="Unable to allocate short code")


@app.get("/{code}")
def redirect_short_url(code: str, db: Session = Depends(get_db)):
    if len(code) > 5:
        raise HTTPException(status_code=404, detail="Not found")

    record = db.scalar(select(URLMap).where(URLMap.code == code))
    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=record.long_url, status_code=307)
