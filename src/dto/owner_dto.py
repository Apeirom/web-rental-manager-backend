from pydantic import BaseModel, ConfigDict
from typing import Optional

class OwnerDTO(BaseModel):
    key: str
    name: str
    document_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)