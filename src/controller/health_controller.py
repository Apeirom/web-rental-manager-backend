from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.repository.health_repository import HealthRepository

class HealthController:
    def __init__(self, db: Session):
        self.health_repository = HealthRepository(db)

    def check_status(self) -> dict:
        try:
            self.health_repository.check_connection()
            return {
                "server": "online",
                "database": "connected"
            }
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="Database connection failed"
            )