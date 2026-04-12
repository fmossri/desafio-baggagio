from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_login_returns_token(client: TestClient, seeded_db: Session) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "admin@exemplo.com", "password": "admin"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

def test_login_invalid_credentials_returns_401_generic(client: TestClient, seeded_db: Session) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "admin@exemplo.com", "password": "wrong_pass"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not authenticate"

def test_auth_me_requires_token(client: TestClient) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_auth_me_with_token_returns_user(client: TestClient, auth_header: dict[str, str]) -> None:
    response = client.get("/auth/me", headers=auth_header)
    assert response.status_code == 200
    body = response.json()
    assert "id" in body
    assert body["email"] == "admin@exemplo.com"
    assert body["is_active"] is True