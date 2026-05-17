from pydantic import BaseModel, ConfigDict

class GuarantorDTO(BaseModel):
    key: str
    name: str
    document_number: str

    model_config = ConfigDict(from_attributes=True)