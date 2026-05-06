from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import URLMapping
from .schemas import URLCreate, URLResponse
from .services import CODE_LENGTH, generate_code

app = FastAPI(title="URL Shortener", version="1.0.0")

Base.metadata.create_all(bind=engine)


@app.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(payload: URLCreate, request: Request, db: Session = Depends(get_db)):
    existing = db.query(URLMapping).filter(URLMapping.original_url == str(payload.url)).first()
    if existing:
        short_url = str(request.base_url) + existing.short_code
        return URLResponse(
            short_code=existing.short_code,
            short_url=short_url,
            original_url=existing.original_url,
        )

    for salt in range(0, 10_000):
        short_code = generate_code(str(payload.url), salt=salt)
        if len(short_code) != CODE_LENGTH:
            continue
        conflict = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
        if conflict:
            continue

        mapping = URLMapping(original_url=str(payload.url), short_code=short_code)
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        short_url = str(request.base_url) + short_code
        return URLResponse(
            short_code=short_code,
            short_url=short_url,
            original_url=mapping.original_url,
        )

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Could not generate unique short code.",
    )


@app.get("/{short_code}")
def redirect_short_url(short_code: str, db: Session = Depends(get_db)):
    if len(short_code) != CODE_LENGTH:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    mapping = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
    if not mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    return RedirectResponse(url=mapping.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
