from fastapi import FastAPI, HTTPException,Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, products
from app.core.config import settings
from app.core.errors import api_error_payload

app = FastAPI(title=settings.app_name, version="0.1.0")

def _cors_origins() -> list[str]:
    raw = settings.cors_origins
    if isinstance(raw, list):
        return raw
    return [x.strip() for x in str(raw).split(",") if x.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

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
        content={"code": "validation_error", "message": "Invalid request", "details": exc.errors()},
    )

app.include_router(auth.router)
app.include_router(products.router)

@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}