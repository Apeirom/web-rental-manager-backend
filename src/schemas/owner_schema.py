from pydantic import BaseModel, Field
from typing import Optional

class OwnerCreateSchema(BaseModel):
    name: str = Field(..., description="Nome completo do proprietário")
    document_number: Optional[str] = Field(None, description="Documento (CPF/CNPJ) do proprietário, opcional")

class OwnerUpdateSchema(BaseModel):
    name: str = Field(..., description="Nome completo do proprietário")
    document_number: Optional[str] = Field(None, description="Documento (CPF/CNPJ) do proprietário, opcional")