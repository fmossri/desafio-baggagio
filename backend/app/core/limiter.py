from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
)

LOGIN_RATE_LIMIT = f"{settings.rate_limit_login_per_minute}/minute"
