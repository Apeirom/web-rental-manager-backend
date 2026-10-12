from sqlalchemy import text
from sqlalchemy.orm import Session

from src.repository.base_repository import BaseRepository


class HealthRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def check_connection(self) -> None:
        self.db.execute(text("SELECT 1"))
