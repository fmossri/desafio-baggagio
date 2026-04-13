from typing import Any


def api_error_payload(
    *,
    code: str,
    message: str,
    details: Any | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        body["details"] = details
    return body