import contextvars
import uuid

request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)

def get_request_id() -> str | None:
    return request_id_ctx.get()

def set_request_id(value: str) -> contextvars.Token:
    return request_id_ctx.set(value)

def reset_request_id(token: contextvars.Token) -> None:
    request_id_ctx.reset(token)

def new_request_id() -> str:
    return str(uuid.uuid4())