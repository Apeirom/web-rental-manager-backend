from pydantic import BaseModel, Field
from typing import Optional

from pydantic import field_validator
from src.utils.document_number import normalize_document_number

class OwnerCreateSchema(BaseModel):
    name: str = Field(..., description="Nome completo do proprietário")
    document_number: Optional[str] = Field(None, description="Documento (CPF/CNPJ) do proprietário, opcional")

    @field_validator("document_number", mode="before")
    @classmethod
    def normalize_optional_document_number(cls, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return normalize_document_number(value)

class OwnerUpdateSchema(BaseModel):
    name: str = Field(..., description="Nome completo do proprietário")
    document_number: Optional[str] = Field(None, description="Documento (CPF/CNPJ) do proprietário, opcional")

    @field_validator("document_number", mode="before")
    @classmethod
    def normalize_optional_document_number(cls, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return normalize_document_number(value)