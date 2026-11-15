from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def client_key(request: Request) -> str:
    """
    Identify the caller for rate limiting.
    Behind a reverse proxy (Railway, etc.) the socket address is the proxy, so
    prefer the first hop of X-Forwarded-For when present.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=client_key)

# Applied to endpoints that call the LLM
CHAT_RATE_LIMIT = f"{settings.RATE_LIMIT_PER_MINUTE}/minute"
