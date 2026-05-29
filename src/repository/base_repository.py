from sqlalchemy.orm import Session
from typing import Type, TypeVar
from src.models.base import Base

T = TypeVar('T', bound=Base) # type: ignore

class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_enumerator_model(self, model_class: Type[T], enumerator: str) -> T:
        instance = self.db.query(model_class).filter(model_class.enumerator == enumerator).first()
        return instance
    
    def commit(self):
        self.db.commit()

    def flush(self):
        self.db.flush()