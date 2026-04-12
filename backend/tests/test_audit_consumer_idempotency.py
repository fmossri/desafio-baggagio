import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

from app.messaging.events import ProductChangedEvent, ProductEventType, ProductSnapshot
from app.workers.audit_consumer import on_message


def _sample_event() -> ProductChangedEvent:
    return ProductChangedEvent(
        event_id=uuid.uuid4(),
        event_type=ProductEventType.CREATED,
        actor_user_id=uuid.uuid4(),
        product=ProductSnapshot(
            id=uuid.uuid4(),
            name="Mala P",
            description="Teste",
            price=Decimal("199.90"),
            quantity=3,
            active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )


def test_duplicate_event_is_acknowledged_twice() -> None:
    event = _sample_event()
    body = json.dumps(event.model_dump(mode="json")).encode("utf-8")

    channel = MagicMock()
    method = MagicMock(delivery_tag=1)
    properties = MagicMock()
    properties.headers = None

    on_message(channel, method, properties, body)
    on_message(channel, method, properties, body)

    assert channel.basic_ack.call_count == 2
    assert channel.basic_nack.call_count == 0