import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from app.messaging.events import ProductEventType, ProductChangedEvent, ProductSnapshot

def _snapshot(**kwargs: Any) -> ProductSnapshot:
    defaults = dict(
        id=uuid.uuid4(),
        name="Mala",
        description="Teste",
        price=Decimal("100.00"),
        quantity=1,
        active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return ProductSnapshot(**defaults) # type: ignore[arg-type]

@pytest.mark.parametrize(
    "event_type, expected_rk",
    [
        (ProductEventType.CREATED, "product.created"),
        (ProductEventType.UPDATED, "product.updated"),
        (ProductEventType.DELETED, "product.deleted"),
    ],
)
def test_routing_key_matches_event_type(event_type: ProductEventType, expected_rk: str) -> None:
    event = ProductChangedEvent(
        event_id=uuid.uuid4(),
        event_type=event_type,
        actor_user_id=uuid.uuid4(),
        product=_snapshot(),
    )
    assert event.routing_key() == expected_rk

def test_product_changed_event_roundtrip_json_mode() -> None:
    event = ProductChangedEvent(
        event_id=uuid.uuid4(),
        event_type=ProductEventType.CREATED,
        actor_user_id=uuid.uuid4(),
        product=_snapshot(),
    )
    dumped = event.model_dump(mode="json")
    restored = ProductChangedEvent.model_validate(dumped)
    assert restored.event_id == event.event_id
    assert restored.event_type == event.event_type
    assert restored.actor_user_id == event.actor_user_id
    assert restored.product.id == event.product.id

def test_invalid_event_type_string_rejected() -> None:
    with pytest.raises(ValidationError):
        ProductChangedEvent.model_validate(
            {
                "event_id": str(uuid.uuid4()),
                "event_type": "invalid",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "actor_user_id": str(uuid.uuid4()),
                "product": _snapshot().model_dump(mode="json"),
            }
        )