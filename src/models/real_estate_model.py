import uuid
from sqlalchemy import Column, Integer, String, Float, Index
from src.models.base import Base

class RealEstateModel(Base):
    __tablename__ = "real_estates"
    __table_args__ = (
        Index("ix_real_estates_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    commission = Column(Float, default=0.0, nullable=False)
    phone = Column(String, nullable=False)