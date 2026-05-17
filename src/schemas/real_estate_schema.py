from pydantic import BaseModel, Field

class RealEstateCreateSchema(BaseModel):
    name: str
    cnpj: str = Field(pattern=r"^(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})$")
    address: str
    commission: float
    phone: str

class RealEstateUpdateSchema(BaseModel):
    name: str
    cnpj: str = Field(pattern=r"^(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})$")
    address: str
    commission: float
    phone: str