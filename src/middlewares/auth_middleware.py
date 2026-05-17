from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.security import verify_jwt_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path not in ["/login", "/docs", "/openapi.json"]:
            token = request.headers.get("Authorization")
            if not token or not verify_jwt_token(token):
                raise HTTPException(status_code=401, detail="Unauthorized")
        
        response = await call_next(request)
        return response