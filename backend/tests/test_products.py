from fastapi.testclient import TestClient

def test_products_require_auth(client: TestClient) -> None:
    response = client.post(
        "/products",
        json={
            "name": "Mala P",
            "description": "Teste",
            "price": "199.90",
            "quantity": 3,
            "active": True,
        },
    )
    assert response.status_code == 401


def test_create_product_with_auth_returns_201(client: TestClient, auth_header: dict[str, str]) -> None:
    response = client.post(
        "/products",
        headers=auth_header,
        json={
            "name": "Mala P",
            "description": "Teste",
            "price": "199.90",
            "quantity": 3,
            "active": True,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Mala P"
    assert body["price"] in ("199.90", 199.9, "199.9")
    assert "id" in body

def test_invalid_product_body_returns_422(client: TestClient, auth_header: dict[str, str]) -> None:
    response = client.post(
        "/products",
        headers=auth_header,
        json={"name": "", "description": "Teste", "price": "199.90", "quantity": -1},
    )
    assert response.status_code == 422
    body = response.json()
    assert body.get("code") == "validation_error"
    assert "message" in body
    assert "details" in body

def test_products_crud_smoke(client: TestClient, auth_header: dict[str, str]) -> None:
    created = client.post(
        "/products",
        headers=auth_header,
        json={
            "name": "Mala G",
            "description": "Teste CRUD",
            "price": "299.90",
            "quantity": 2,
            "active": True,
        },
    )
    # Create
    assert created.status_code == 201
    product_id = created.json()["id"]

    # Lista
    listed = client.get("/products", headers=auth_header)
    assert listed.status_code == 200
    assert isinstance(listed.json(), list)

    # Get
    got = client.get(f"/products/{product_id}", headers=auth_header)
    assert got.status_code == 200

    # Update
    updated = client.put(
        f"/products/{product_id}",
        headers=auth_header,
        json={"quantity": 7},
    )

    assert updated.status_code == 200
    assert updated.json()["quantity"] == 7

    # Delete
    deleted = client.delete(f"/products/{product_id}", headers=auth_header)
    assert deleted.status_code == 204

    # Get depois de delete deve retornar 404
    got_after_delete = client.get(f"/products/{product_id}", headers=auth_header)
    assert got_after_delete.status_code == 404

    # Lista depois do delete deve retornar vazia
    listed_after_delete = client.get("/products", headers=auth_header)
    assert listed_after_delete.status_code == 200
    assert listed_after_delete.json() == []