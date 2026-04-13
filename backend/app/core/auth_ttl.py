import time

from app.core.config import settings


def refresh_ttl_seconds() -> int:
    return settings.refresh_token_expire_days * 86400

def access_deny_ttl_seconds_from_payload(payload: dict) -> int:
    exp = int(payload["exp"])
    ttl = exp - int(time.time())
    return max(1, ttl)