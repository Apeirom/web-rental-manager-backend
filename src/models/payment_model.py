import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    payment_date = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

    status_id = Column(Integer, ForeignKey("payment_statuses.id"), nullable=False)
    status = relationship("PaymentStatusModel")

    extract_id = Column(Integer, ForeignKey("extracts.id"), nullable=True)
    extract = relationship("ExtractModel")