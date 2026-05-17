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
    receipt_path = Column(String, nullable=True)
    iptu = Column(Float, default=0.0, nullable=False)
    water = Column(Float, default=0.0, nullable=False)
    agreement = Column(Float, default=0.0, nullable=False)

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    contract = relationship("ContractModel")