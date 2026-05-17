from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException

class HealthController:
    def __init__(self, db: Session):
        self.db = db

    def check_status(self) -> dict:
        try:
            self.db.execute(text("SELECT 1"))
            return {
                "server": "online",
                "database": "connected"
            }
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="Database connection failed"
            )