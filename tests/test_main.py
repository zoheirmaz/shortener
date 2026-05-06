from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app, get_db

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
