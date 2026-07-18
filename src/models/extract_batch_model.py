# src/models/extract_batch_model.py
import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class ExtractBatchModel(Base):
    __tablename__ = "extract_batches"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    total_net_transfer = Column(Float, default=0.0, nullable=False)    
    file_path = Column(String, nullable=True)

    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True, unique=True)
    payment = relationship("PaymentModel", back_populates="extract_batch", uselist=False)

    extracts = relationship("ExtractModel", back_populates="batch", cascade="all, delete-orphan")

    @property
    def status(self) -> str:
        return 'linked' if self.payment_id else 'unlinked'