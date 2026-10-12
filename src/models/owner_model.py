import uuid
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.models.base import Base

class OwnerModel(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    document_number = Column(String, nullable=True)

    properties = relationship(
        "PropertyModel",
        back_populates="owner",
        cascade="all, delete-orphan",
    )