from src.models.base import Base
from src.models.enumerator_minxin_model import EnumeratorMixin

class ExtractItemCategoryModel(Base, EnumeratorMixin):
    __tablename__ = "extract_item_categories"