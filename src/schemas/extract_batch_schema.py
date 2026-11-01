from pydantic import BaseModel
from typing import Optional, List
from src.schemas.extract_schema import ExtractCreateSchema, ExtractUpdateSchema

class ExtractBatchCreateSchema(BaseModel):
    file_path: Optional[str] = None
    extracts: List[ExtractCreateSchema]
    confirm_duplicate: Optional[bool] = False

class ExtractBatchUpdateSchema(BaseModel):
    file_path: Optional[str] = None
    extracts: List[ExtractUpdateSchema]
