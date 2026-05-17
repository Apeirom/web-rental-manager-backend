from pydantic import BaseModel, Field

class GuarantorCreateSchema(BaseModel):
    name: str
    document_number: str = Field(
        pattern=r"^(\d{2,3}(\.\d{3}){2}\/\d{4}-\d{2}|\d{3}(\.\d{3}){2}-\d{2})$"
    )

class GuarantorUpdateSchema(BaseModel):
    name: str
    document_number: str = Field(
        pattern=r"^(\d{2,3}(\.\d{3}){2}\/\d{4}-\d{2}|\d{3}(\.\d{3}){2}-\d{2})$"
    )