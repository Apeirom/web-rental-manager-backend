import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    payment_date = Column(String, nullable=False)
    month_ref = Column(Integer, nullable=False)
    year_ref = Column(Integer, nullable=False)
    receipt_path = Column(String, nullable=True)

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    contract = relationship("ContractModel")