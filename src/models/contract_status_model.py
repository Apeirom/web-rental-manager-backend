from sqlalchemy import Column, Integer, String
from src.models.base import Base
from src.models.enumerator_minxin_model import EnumeratorMixin

class ContractStatusModel(Base, EnumeratorMixin):
    __tablename__ = "contract_statuses"