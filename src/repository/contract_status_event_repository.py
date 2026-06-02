from sqlalchemy.orm import Session
from src.repository.base_repository import BaseRepository 
from src.models import ContractModel, ContractStatusEventModel, ContractStatusModel


class ContractStatusEventRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        
    def create(self, contract: ContractModel, status: ContractStatusModel, user_data: dict) -> ContractStatusEventModel:
        event = ContractStatusEventModel(
            contract = contract,
            status=status,
            user_data=user_data
        )
        self.db.add(event)
        self.db.flush()
        return event

    def delete(self, event_model: ContractStatusEventModel) -> None:
        self.db.delete(event_model)
        self.db.flush()