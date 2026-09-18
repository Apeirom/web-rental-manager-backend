from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request

def get_user_or_ip(request: Request) -> str:
    if hasattr(request.state, "user") and request.state.user:
        return str(request.state.user.get("key"))
    
    return get_remote_address(request)

limiter = Limiter(
    key_func=get_user_or_ip,
    default_limits=["120/minute"]
)

def setup_rate_limit(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)