import uuid
from sqlalchemy import Column, Integer, String, Float
from src.models.base import Base

class BailInsuranceModel(Base):
    __tablename__ = "bail_insurances"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    value = Column(Float, nullable=False)
    validity = Column(String, nullable=False)
    insurance_company = Column(String, nullable=False)