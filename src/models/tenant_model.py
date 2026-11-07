import uuid
from sqlalchemy import Column, Integer, String, Index
from src.models.base import Base

class TenantModel(Base):
    __tablename__ = "tenants"
    __table_args__ = (
        Index("ix_tenants_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    document_number = Column(String, unique=True, nullable=False)