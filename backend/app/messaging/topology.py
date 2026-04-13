from pika.adapters.blocking_connection import BlockingChannel

from app.core.config import settings
import app.messaging.constants as cons


def declare_topology(channel: BlockingChannel) -> None:
    channel.exchange_declare(
        exchange=cons.EXCHANGE_PRODUCTS,
        exchange_type="topic",
        durable=True,
    )
    channel.exchange_declare(
        exchange=cons.EXCHANGE_DLX,
        exchange_type="direct",
        durable=True,
    )
    channel.queue_declare(
        queue=cons.QUEUE_AUDIT_MAIN,
        durable=True,
        arguments={
            "x-dead-letter-exchange": cons.EXCHANGE_DLX,
            "x-dead-letter-routing-key": cons.ROUTING_RETRY,
        }
    )
    channel.queue_bind(
        queue=cons.QUEUE_AUDIT_MAIN,
        exchange=cons.EXCHANGE_PRODUCTS,
        routing_key=cons.ROUTING_PRODUCT_ALL,
    )
    channel.queue_bind(
        queue=cons.QUEUE_AUDIT_MAIN,
        exchange=cons.EXCHANGE_PRODUCTS,
        routing_key=cons.ROUTING_REDELIVER,
    )

    channel.queue_declare(
        queue=cons.QUEUE_AUDIT_RETRY,
        durable=True,
        arguments={
            "x-message-ttl": settings.messaging_retry_ttl_ms,
            "x-dead-letter-exchange": cons.EXCHANGE_PRODUCTS,
            "x-dead-letter-routing-key": cons.ROUTING_REDELIVER,
        },
    )
    channel.queue_bind(
        queue=cons.QUEUE_AUDIT_RETRY,
        exchange=cons.EXCHANGE_DLX,
        routing_key=cons.ROUTING_RETRY,
    )

    channel.queue_declare(queue=cons.QUEUE_AUDIT_DLQ, durable=True)
    channel.queue_bind(
        queue=cons.QUEUE_AUDIT_DLQ,
        exchange=cons.EXCHANGE_DLX,
        routing_key=cons.ROUTING_DLQ,
    )