import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.request_context import new_request_id, set_request_id, reset_request_id

REQUEST_ID_HEADER = "X-Request-ID"

logger = logging.getLogger("app.request")

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        incoming = request.headers.get(REQUEST_ID_HEADER)
        rid = incoming.strip() if incoming and incoming.strip() else new_request_id()
        token = set_request_id(rid)
        try:
            response: Response = await call_next(request)
            logger.info("request_completed", extra={"path": request.url.path, "method": request.method})
            response.headers[REQUEST_ID_HEADER] = rid
            return response
        finally:
            reset_request_id(token)