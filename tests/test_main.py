from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models import CodePool
from app.repositories.sqlalchemy_code_pool_repository import SQLAlchemyCodePoolRepository

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_shortener.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def seed_code_pool():
    from app.models import URLMap

    db = TestingSessionLocal()
    db.query(CodePool).delete()
    db.query(URLMap).delete()
    db.commit()

    repository = SQLAlchemyCodePoolRepository(session=db)
    repository.seed_code_pool(target_available=10)
    db.close()
    yield

    db = TestingSessionLocal()
    db.query(CodePool).delete()
    db.query(URLMap).delete()
    db.commit()
    db.close()


def test_shorten_url_returns_code():
    response = client.post("/shorten", json={"url": "https://example.com/some/very/long/path"})
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert len(data["code"]) <= 5
    assert data["original_url"] == "https://example.com/some/very/long/path"


def test_redirect_short_url():
    create_response = client.post("/shorten", json={"url": "https://openai.com/research"})
    code = create_response.json()["code"]

    redirect_response = client.get(f"/{code}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://openai.com/research"


def test_shorten_url_no_available_codes():
    db = TestingSessionLocal()
    db.query(CodePool).delete()
    db.commit()
    db.close()

    response = client.post("/shorten", json={"url": "https://example.com/test"})
    assert response.status_code == 503
    assert response.json()["detail"] == "No available short codes"


def test_duplicate_url_returns_409():
    url = "https://example.com/duplicate"
    client.post("/shorten", json={"url": url})

    response = client.post("/shorten", json={"url": url})
    assert response.status_code == 409


def test_release_stale_reserved_codes():
    db = TestingSessionLocal()
    repository = SQLAlchemyCodePoolRepository(session=db)

    db.query(CodePool).delete()
    db.commit()

    repository.seed_code_pool(target_available=5)

    stale_code = db.query(CodePool).first()
    stale_code.status = "reserved"
    stale_code.reserved_at = datetime.now(timezone.utc) - timedelta(seconds=400)
    db.commit()

    released = repository.release_stale_reserved_codes(reserved_timeout_seconds=300)
    assert released == 1

    stale_code_after = db.query(CodePool).filter(CodePool.code == stale_code.code).first()
    assert stale_code_after.status == "available"
    assert stale_code_after.reserved_at is None

    db.close()
