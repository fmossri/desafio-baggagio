import json
import logging

import pika
from pika.exceptions import AMQPError

from app.core.config import settings
from app.messaging.constants import EXCHANGE_PRODUCTS
from app.messaging.events import ProductChangedEvent
from app.messaging.topology import declare_topology

logger = logging.getLogger(__name__)


class ProductEventPublisher:
    def __init__(self, rabbitmq_url: str | None = None) -> None:
        self._url = rabbitmq_url or settings.rabbitmq_url

    def publish(self, event: ProductChangedEvent) -> None:
        params = pika.URLParameters(self._url)
        connection = pika.BlockingConnection(params)

        try:
            channel = connection.channel()

            declare_topology(channel)

            payload = json.dumps(event.model_dump(mode="json"))

            channel.basic_publish(
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
                    "routing_key": event.routing_key()
                }
            )

        except AMQPError as e:
            logger.exception(
                "failed_to_publish_product_event",
                extra={
                    "event_id": str(event.event_id),
                    "event_type": event.event_type.value,
                    "error": str(e),
                }
            )
            raise
        
        finally:
            if connection.is_open:
                connection.close()
        