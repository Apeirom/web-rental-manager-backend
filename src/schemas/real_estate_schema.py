from pydantic import BaseModel, field_validator

from src.utils.document_number import normalize_cnpj

class RealEstateCreateSchema(BaseModel):
    name: str
    cnpj: str
    address: str
    commission: float
    phone: str

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, value):
        return normalize_cnpj(value)

class RealEstateUpdateSchema(BaseModel):
    name: str
    cnpj: str
    address: str
    commission: float
    phone: str

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, value):
        return normalize_cnpj(value)