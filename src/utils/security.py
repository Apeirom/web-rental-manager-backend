import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, status
from src.errors.custom_errors import NotProvidedCredentials



from src.constants import JWT_SECRET, JWT_ALGORITHM 

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def create_access_token(data: dict, expires_delta_hours: int = 3) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=expires_delta_hours)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_user_info_by_token(request: Request) -> dict:
    if not hasattr(request.state, "user"):
        raise NotProvidedCredentials()
        
    payload = request.state.user
    
    return {
        "key": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role")
    }