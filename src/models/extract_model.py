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
    
    rent_amount = Column(Float, default=0.0, nullable=False)
    iptu = Column(Float, default=0.0, nullable=False)
    water = Column(Float, default=0.0, nullable=False)
    maintenance = Column(Float, default=0.0, nullable=False)
    agreement = Column(Float, default=0.0, nullable=False)
    penalty = Column(Float, default=0.0, nullable=False)
    interest = Column(Float, default=0.0, nullable=False)
    other_revenues = Column(Float, default=0.0, nullable=False)

    administration_fee = Column(Float, default=0.0, nullable=False)
    bank_fee = Column(Float, default=0.0, nullable=False)

    net_transfer = Column(Float, default=0.0, nullable=False)

    file_path = Column(String, nullable=True)

    payment = relationship("PaymentModel", back_populates="extract", uselist=False)

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    contract = relationship("ContractModel")