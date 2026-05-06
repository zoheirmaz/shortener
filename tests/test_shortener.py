from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_shortener.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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


def test_shorten_url_and_redirect():
    response = client.post("/shorten", json={"url": "https://example.com/long/path"})
    assert response.status_code == 201

    data = response.json()
    assert len(data["short_code"]) == 5
    assert data["original_url"] == "https://example.com/long/path"

    redirect_response = client.get(f"/{data['short_code']}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/long/path"


def test_invalid_url_validation_error():
    response = client.post("/shorten", json={"url": "invalid-url"})
    assert response.status_code == 422
