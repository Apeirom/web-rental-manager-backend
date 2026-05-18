from pydantic import BaseModel, ConfigDict

class UserDTO(BaseModel):
    key: str
    name: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)

class TokenDTO(BaseModel):
    access_token: str
    token_type: str