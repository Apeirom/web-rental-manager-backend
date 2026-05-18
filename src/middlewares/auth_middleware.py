import os
import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = ["/auth/login", "/docs", "/openapi.json"]
        
        if request.url.path not in public_paths and request.method != "OPTIONS":
            auth_header = request.headers.get("Authorization")
            
            if not auth_header:
                return JSONResponse(status_code=401, content={"detail": "Missing authorization header"})
            
            try:
                scheme, token = auth_header.split()
                if scheme.lower() != "bearer":
                    raise ValueError
                
                payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
                request.state.user = payload 
                
            except Exception:
                return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})
                
        response = await call_next(request)
        return response