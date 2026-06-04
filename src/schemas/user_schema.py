from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreateSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserRoleUpdateSchema(BaseModel):
    role: str