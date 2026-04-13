import logging
import sys

from pythonjsonlogger.jsonlogger import JsonFormatter as JsonLoggerFormatter

from app.core.request_context import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        rid = get_request_id()
        record.request_id = rid if rid else "-"
        return True


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonLoggerFormatter(
        "%(timestamp)s %(levelname)s %(name)s %(message)s %(request_id)s",
        timestamp=True,
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

class WorkerLoggingFilter(logging.Filter):
    def __init__(self, service_name: str) -> None:
        super().__init__()
        self._service_name = service_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.service = self._service_name
        return True

def configure_worker_logging(*, service_name: str = "audit_consumer", level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonLoggerFormatter(
        "%(timestamp)s %(levelname)s %(name)s %(message)s %(service)s",
        timestamp=True,
    )
    handler.setFormatter(formatter)
    handler.addFilter(WorkerLoggingFilter(service_name))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    logging.getLogger("pika").setLevel(logging.WARNING)

