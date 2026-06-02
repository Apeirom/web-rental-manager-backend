from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponseDTO(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    data: list[T]