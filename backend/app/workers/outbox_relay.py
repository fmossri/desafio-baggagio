import json
import logging
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import SessionLocal
from app.messaging.events import ProductChangedEvent
from app.messaging.publisher import ProductEventPublisher
from app.models.outbox_event import OutboxEvent

logger = logging.getLogger(__name__)


def _to_event(row: OutboxEvent) -> ProductChangedEvent:
    payload = row.payload
    if isinstance(payload, str):
        payload = json.loads(payload)
    return ProductChangedEvent.model_validate(payload)


def run_once(db: Session, publisher: ProductEventPublisher) -> int:
    statement = (
        select(OutboxEvent)
        .where(OutboxEvent.published_at.is_(None))
        .order_by(OutboxEvent.created_at.asc())
        .limit(settings.outbox_batch_size)
    )
    rows = db.execute(statement).scalars().all()
    if not rows:
        return 0

    processed = 0
    for row in rows:
        try:
            event = _to_event(row)
            publisher.publish(event)
            row.published_at = datetime.now(timezone.utc)
            row.last_error = None
            processed += 1

            logger.info(
                "outbox_event_published",
                extra={
                    "outbox_id": str(row.id),
                    "event_id": str(event.event_id),
                    "event_type": event.event_type.value,
                }
            )

        except Exception as e:
            row.attempt_count = (row.attempt_count or 0) + 1
            row.last_error = str(e)[:2000]

            logger.exception(
                "outbox_evennt_publish_failed",
                extra={
                    "outbox_id": str(row.id),
                    "event_type": row.event_type,
                    "attempt_count": row.attempt_count
                }
            )

        finally:
            db.commit()

    return processed


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("outbox_relay_started")

    publisher = ProductEventPublisher()

    while True:
        db = SessionLocal()
        try:
            sent = run_once(db, publisher)
            if sent == 0:
                time.sleep(settings.outbox_poll_interval_seconds)
        except Exception:
            logger.exception("outbox_relay_loop_failed")
        finally:
            db.close()

if __name__ == "__main__":
    main()