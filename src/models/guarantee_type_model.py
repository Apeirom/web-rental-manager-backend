from sqlalchemy import Column, Integer, String
from src.models.base import Base

class GuaranteeTypeModel(Base):
    __tablename__ = "guarantee_types"

    id = Column(Integer, primary_key=True, index=True)
    enumerator = Column(String, unique=True, nullable=False)

