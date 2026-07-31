import uuid
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class ExtractItemModel(Base):
    __tablename__ = "extract_items"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    is_credit = Column(Boolean, nullable=False)
    is_withheld_at_source = Column(Boolean, nullable=False, default=False)
    
    extract_id = Column(Integer, ForeignKey("extracts.id"), nullable=False)
    extract = relationship("ExtractModel", back_populates="items")

    category_id = Column(Integer, ForeignKey("extract_item_categories.id"), nullable=False)
    category = relationship("ExtractItemCategoryModel")