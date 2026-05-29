import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.constants import JWT_SECRET, JWT_ALGORITHM

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = ["/auth/login", "/docs", "/openapi.json", "/health", "/"]
        
        if request.url.path not in public_paths and request.method != "OPTIONS":
            auth_header = request.headers.get("Authorization")
            
            if not auth_header:
                return JSONResponse(status_code=401, content={"detail": "Missing authorization header"})
            
            try:
                scheme, token = auth_header.split()
                if scheme.lower() != "bearer":
                    raise ValueError
                
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                request.state.user = payload 
                
            except ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token expired"})
            except InvalidTokenError:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})
            except Exception:
                return JSONResponse(status_code=401, content={"detail": "Authentication failed"})
                
        response = await call_next(request)
        return response