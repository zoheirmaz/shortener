from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.dependencies import get_code_pool_repository, get_url_repository
from app.repositories.interfaces import CodePoolRepository, URLRepository
from app.schemas import ShortenRequest, ShortenResponse
from app.validators import ShortCodeParam

app = FastAPI(title="URL Shortener", version="1.0.0")


@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(
    payload: ShortenRequest,
    request: Request,
    url_repository: URLRepository = Depends(get_url_repository),
    code_pool_repository: CodePoolRepository = Depends(get_code_pool_repository),
):
    long_url = str(payload.url)

    code = code_pool_repository.allocate_code()
    if not code:
        raise HTTPException(status_code=503, detail="No available short codes")

    record = url_repository.create(code=code, long_url=long_url)
    code_pool_repository.mark_used(code)

    return ShortenResponse(
        short_url=f'/{record.code}',
        code=record.code,
        original_url=record.long_url,
    )


@app.get("/{code}")
def redirect_short_url(
    code: ShortCodeParam,
    url_repository: URLRepository = Depends(get_url_repository),
):
    record = url_repository.get_by_code(code)
    if not record:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(
        url=record.long_url,
        status_code=301,
        headers={"Cache-Control": "public, max-age=86400"}
    )
