import uuid
from sqlalchemy import Column, Integer, String
from src.models.base import Base

class GuarantorModel(Base):
    __tablename__ = "guarantors"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    document_number = Column(String, unique=True, nullable=False)