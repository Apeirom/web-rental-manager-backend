import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class ExtractModel(Base):
    __tablename__ = "extracts"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    month_ref = Column(Integer, nullable=False)
    year_ref = Column(Integer, nullable=False)
    
    net_transfer = Column(Float, default=0.0, nullable=False)

    extract_batch_id = Column(Integer, ForeignKey("extract_batches.id"), nullable=False)
    batch = relationship("ExtractBatchModel", back_populates="extracts")

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    contract = relationship("ContractModel")

    items = relationship("ExtractItemModel", back_populates="extract", cascade="all, delete-orphan")