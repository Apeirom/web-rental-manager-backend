from pydantic import BaseModel, Field

class UserCreateSchema(BaseModel):
    name: str
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str

class UserLoginSchema(BaseModel):
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str