from pydantic import BaseModel, field_validator

from src.utils.document_number import normalize_document_number

class TenantCreateSchema(BaseModel):
    name: str
    document_number: str

    @field_validator("document_number")
    @classmethod
    def validate_document_number(cls, value):
        return normalize_document_number(value)

class TenantUpdateSchema(BaseModel):
    name: str
    document_number: str

    @field_validator("document_number")
    @classmethod
    def validate_document_number(cls, value):
        return normalize_document_number(value)