import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

test_db_url = os.getenv("TEST_DATABASE_URL")
if not test_db_url:
    raise RuntimeError("TEST_DATABASE_URL não configurado (setar em docker-compose - test service).")

os.environ["DATABASE_URL"] = test_db_url
os.environ.setdefault("JWT_SECRET_KEY", "test-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

from app.api.deps import get_db
from app.db import Base
from app.main import app
from scripts.seed_admin import run as seed_admin

engine = create_engine(test_db_url, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def _clean_products_and_messaging(db_session: Session) -> Generator[None, None, None]:
    db_session.execute(
        text(
            "TRUNCATE TABLE products, outbox_events, processed_events " 
            "RESTART IDENTITY CASCADE"
        )
    )
    db_session.commit()
    yield

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def seeded_db(db_session: Session) -> Session:
    seed_admin(db_session)
    return db_session

@pytest.fixture(scope="function")
def auth_header(client: TestClient, seeded_db: Session) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": "admin@exemplo.com", "password": "admin"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}