import json
import logging
import time
import uuid
from collections.abc import Mapping
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError
from pika.spec import Basic, BasicProperties
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import SessionLocal
from app.messaging.constants import EXCHANGE_DLX, QUEUE_AUDIT_MAIN, ROUTING_DLQ
from app.messaging.events import ProductChangedEvent
from app.messaging.topology import declare_topology
from app.models import ProcessedEvent

logger = logging.getLogger(__name__)


def _x_death_count(headers: Mapping[str, Any] | None) -> int:
    if not headers:
        return 0
        
    x_death = headers.get("x-death", [])
    total = 0
    if isinstance(x_death, list):
        for item in x_death:
            if isinstance(item, Mapping):
                total += item.get("count", 0)
    return total


def _send_to_dlq(channel: BlockingChannel, body: bytes, props: BasicProperties | None) -> None:
    headers = props.headers if props and props.headers else {}
    channel.basic_publish(
        exchange=EXCHANGE_DLX,
        routing_key=ROUTING_DLQ,
        body=body,
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
            message_id=getattr(props, "message_id", None),
            headers=headers,
        ),
        mandatory=False,
    )

def on_message(
    channel: BlockingChannel,
    method: Basic.Deliver,
    properties: BasicProperties,
    body: bytes,
) -> None:
    death_count = _x_death_count(properties.headers if properties else None)

    if death_count >= settings.messaging_max_attempts:
        _send_to_dlq(channel, body, properties)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.warning("event_sent_to_dlq_after_retry_cap", extra={"x_death_count": death_count})
        return

    db: Session = SessionLocal()
    try:
        payload = json.loads(body.decode("utf-8"))
        event = ProductChangedEvent.model_validate(payload)

        db.add(ProcessedEvent(event_id=uuid.UUID(str(event.event_id))))
        db.commit()

        logger.info(
            "product_event_processed",
            extra={
                "event_id": str(event.event_id),
                "event_type": event.event_type.value,
                "actor_user_id": str(event.actor_user_id),
                "product_id": str(event.product.id)
            }
        )

        channel.basic_ack(delivery_tag=method.delivery_tag)

    except IntegrityError:
        db.rollback()
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("duplicate_event_skipped")

    except Exception:
        db.rollback()
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        logger.exception("consumer_transiennt_failure_nacked")

    finally:
        db.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("audit_consumer_started")

    while True:
        try:
            params = pika.URLParameters(settings.rabbitmq_url)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            declare_topology(channel)
            channel.basic_qos(prefetch_count=10)
            channel.basic_consume(
                queue=QUEUE_AUDIT_MAIN,
                on_message_callback=on_message,
                auto_ack=False,
            )    

            logger.info("audit_consumer_waiting_for_messages")
            channel.start_consuming()

        except AMQPConnectionError:
            logger.exception("audit_consumer_broker_unreachable_retrying")
            time.sleep(3)

        except Exception:
            logger.exception("audit_consumer_unexpected_error_retrying")
            time.sleep(3)


if __name__ == "__main__":
    main()