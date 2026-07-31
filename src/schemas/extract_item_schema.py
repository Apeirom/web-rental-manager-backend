from typing import Optional
from pydantic import BaseModel

class ExtractItemCreateSchema(BaseModel):
    category: str
    description: str
    amount: float
    is_credit: bool
    is_withheld_at_source: bool = False

class ExtractItemUpdateSchema(ExtractItemCreateSchema):
    key: Optional[str] = None