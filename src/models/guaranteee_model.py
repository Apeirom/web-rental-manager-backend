import uuid
from sqlalchemy import Boolean, Column, Date, Integer, String, Float, ForeignKey
from src.models.base import Base

class GuaranteeModel(Base):
    __tablename__ = "guarantees"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(50), nullable=False)

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "base",
    }

class DepositModel(GuaranteeModel):
    __tablename__ = "guarantee_deposits"
    id = Column(Integer, ForeignKey("guarantees.id", ondelete="CASCADE"), primary_key=True)
    
    amount = Column(Float, nullable=False)
    paid_in_cash = Column(Boolean, default=False)
    deposit_date = Column(Date, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "deposit"}

class GuarantorModel(GuaranteeModel):
    __tablename__ = "guarantee_guarantors"
    id = Column(Integer, ForeignKey("guarantees.id", ondelete="CASCADE"), primary_key=True)
    
    name = Column(String, nullable=False)
    document_number = Column(String, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "guarantor"}

class BailInsuranceModel(GuaranteeModel):
    __tablename__ = "guarantee_bail_insurances"
    id = Column(Integer, ForeignKey("guarantees.id", ondelete="CASCADE"), primary_key=True)
    
    value = Column(Float, nullable=False)
    validity = Column(String, nullable=False)
    insurance_company = Column(String, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "bail_insurance"}
