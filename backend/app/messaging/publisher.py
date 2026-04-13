import json
import logging

import pika
from pika.exceptions import AMQPError, StreamLostError
from pika.adapters.blocking_connection import BlockingChannel

from app.core.config import settings
from app.messaging.constants import EXCHANGE_PRODUCTS
from app.messaging.events import ProductChangedEvent
from app.messaging.topology import declare_topology

logger = logging.getLogger(__name__)


class ProductEventPublisher:
    def __init__(self, rabbitmq_url: str | None = None) -> None:
        self._url = rabbitmq_url or settings.rabbitmq_url
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def _ensure_channel(self) -> None:
        if (
            self._connection
            and self._connection.is_open
            and self._channel
            and self._channel.is_open
        ):
            return
        self.close()
        params = pika.URLParameters(self._url)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        declare_topology(self._channel)

    def close(self) -> None:
        try:
            if self._channel and self._channel.is_open:
                self._channel.close()
        except Exception:
            logger.exception("publisher_channel_close_failed")
        self._channel = None
        try:
            if self._connection and self._connection.is_open:
                self._connection.close()
        except Exception:
            logger.exception("publisher_connection_close_failed")
        self._connection = None

    def publish(self, event: ProductChangedEvent) -> None:
        payload = json.dumps(event.model_dump(mode="json"))
        try:
            self._ensure_channel()
            assert self._channel is not None
            self._channel.basic_publish(
                exchange=EXCHANGE_PRODUCTS,
                routing_key=event.routing_key(),
                body=payload,
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                    message_id=str(event.event_id),
                    timestamp=int(event.occurred_at.timestamp()),
                ),
                mandatory=False,
            )
            logger.info(
                "published_product_event",
                extra={
                    "event_id": str(event.event_id),
                    "event_type": event.event_type.value,
                    "routing_key": event.routing_key(),
                },
            )
        except (AMQPError, StreamLostError):
            logger.exception(
                "failed_to_publish_product_event",
                extra={
                    "event_id": str(event.event_id),
                    "event_type": event.event_type.value,
                },
            )
            self.close()
            raise
   