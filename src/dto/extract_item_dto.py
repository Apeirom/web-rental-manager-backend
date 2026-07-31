from pydantic import BaseModel, ConfigDict
from src.dto.base_enumerator_dto import EnumeratorString

class ExtractItemDTO(BaseModel):
    key: str
    description: str
    amount: float
    is_credit: bool
    is_withheld_at_source: bool
    
    category: EnumeratorString
    
    model_config = ConfigDict(from_attributes=True)