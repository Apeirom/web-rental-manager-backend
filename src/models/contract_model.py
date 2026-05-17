import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class ContractModel(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    guarantee = Column(String, nullable=False)
    rental_deposit = Column(Float, default=0.0)
    rent_amount = Column(Float, nullable=False)
    room_name = Column(String, nullable=True)
    acting = Column(String, default="active")
    file_path = Column(String, nullable=True)

    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    real_estate_id = Column(Integer, ForeignKey("real_estates.id"), nullable=True)
    guarantor_id = Column(Integer, ForeignKey("guarantors.id"), nullable=True)
    bail_insurance_id = Column(Integer, ForeignKey("bail_insurances.id"), nullable=True)

    property = relationship("PropertyModel")
    tenant = relationship("TenantModel")
    real_estate = relationship("RealEstateModel")
    guarantor = relationship("GuarantorModel")
    bail_insurance = relationship("BailInsuranceModel")