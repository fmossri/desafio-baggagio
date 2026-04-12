import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models import OutboxEvent, User, Product
from app.messaging.events import ProductChangedEvent


def _product_json(
    *,
    name: str = "Mala P",
    description: str = "Teste",
    price: str = "199.90",
    quantity: int = 3,
    active: bool = True,
) -> dict[str, str | int | bool]:
    return {
        "name": name,
        "description": description,
        "price": price,
        "quantity": quantity,
        "active": active,
    }

def test_create_product_inserts_outbox_row(
    client: TestClient, auth_header: dict[str, str], db_session: Session
) -> None:
    response = client.post(
        "/products",
        headers=auth_header,
        json=_product_json(name="Mochila de Viagem", price="600.90", quantity=1),
    )
    assert response.status_code == 201
    product_id = uuid.UUID(response.json()["id"])

    rows = db_session.execute(
        select(OutboxEvent).where(OutboxEvent.aggregate_id == product_id)
    ).scalars().all()
    assert len(rows) == 1
    assert rows[0].event_type == "product.created"
    assert rows[0].aggregate_type == "product"

    payload = ProductChangedEvent.model_validate(rows[0].payload)
    assert payload.product.id == product_id
    assert payload.event_type.value == "product.created"


def test_update_product_inserts_outbox_row(
    client: TestClient, auth_header: dict[str, str], db_session: Session
) -> None:
    created = client.post(
        "/products",
        headers=auth_header,
        json=_product_json(),
    )
    assert created.status_code == 201
    product_id = uuid.UUID(created.json()["id"])

    updated = client.put(
        f"/products/{product_id}",
        headers=auth_header,
        json=_product_json(quantity=5),
    )
    assert updated.status_code == 200

    rows = (
        db_session.execute(
            select(OutboxEvent).where(OutboxEvent.aggregate_id == product_id)
        )
        .scalars()
        .all()
    )
    assert len(rows) == 2
    types = {row.event_type for row in rows}
    assert types == {"product.created", "product.updated"}


def test_delete_product_inserts_outbox_row_before_removal(
    client: TestClient, auth_header: dict[str, str], db_session: Session
) -> None:
    created = client.post(
        "/products",
        headers=auth_header,
        json=_product_json(),
    )
    assert created.status_code == 201
    product_id = uuid.UUID(created.json()["id"])
    
    deleted = client.delete(
        f"/products/{product_id}",
        headers=auth_header,
    )
    assert deleted.status_code == 204

    rows = (
        db_session.execute(
            select(OutboxEvent).where(OutboxEvent.aggregate_id == product_id)
        )
        .scalars()
        .all()
    )
    assert len(rows) == 2
    types = {row.event_type for row in rows}
    assert types == {"product.created", "product.deleted"}

    deleted_payload = next(row for row in rows if row.event_type == "product.deleted")
    event = ProductChangedEvent.model_validate(deleted_payload.payload)
    assert event.product.id == product_id


def test_create_product_sets_created_by_to_admin_user(
    client: TestClient, auth_header: dict[str, str], db_session: Session
) -> None:
    admin = db_session.execute(
        select(User).where(User.email == "admin@exemplo.com")
    ).scalar_one()

    response = client.post(
        "/products",
        headers=auth_header,
        json=_product_json(),
    )
    assert response.status_code == 201
    product_id = uuid.UUID(response.json()["id"])

    product = db_session.get(Product, product_id)
    assert product is not None
    assert product.created_by == admin.id