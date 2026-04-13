from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.api.deps import get_db
from app.api.routes import auth, products
from app.core.config import settings
from app.core.errors import api_error_payload
from app.core.limiter import limiter
from app.core.logging_config import configure_logging
from app.core.middleware.request_id import REQUEST_ID_HEADER, RequestIdMiddleware
from app.core.middleware.security_headers import SecurityHeadersMiddleware
from app.core.redis_client import get_redis


def rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    if not isinstance(exc, RateLimitExceeded):
        raise exc
    return _rate_limit_exceeded_handler(request, exc)


configure_logging()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

def _cors_origins() -> list[str]:
    raw = settings.cors_origins
    if isinstance(raw, list):
        return raw
    return [x.strip() for x in str(raw).split(",") if x.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", REQUEST_ID_HEADER],
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


def _default_code_for_status(status_code: int) -> str:
    match status_code:
        case 400:
            return "bad_request"
        case 401:
            return "unauthenticated"
        case 403:
            return "forbidden"
        case 404:
            return "not_found"
        case 409:
            return "conflict"
        case 422:
            return "validation_error"
        case _:
            return "error"

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, str):
        message = detail
        details = None
    elif isinstance(detail, (list, dict)):
        message = "Request failed"
        details = detail
    else:
        message = "Request failed"
        details = None

    code = _default_code_for_status(exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content=api_error_payload(code=code, message=message, details=details),
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=api_error_payload(
            code="validation_error",
            message="Invalid request",
            details=exc.errors(),
        ),
    )

app.include_router(auth.router)
app.include_router(products.router)

@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/ready", tags=["health"])
def ready(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        r = get_redis()
        r.ping()
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable")
    return {"status": "ready"}