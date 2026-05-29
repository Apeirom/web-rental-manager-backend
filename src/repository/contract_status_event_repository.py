from sqlalchemy.orm import Session
from src.repository.enumerator_repository import EnumeratorRepository
from src.models.contract_status_event_model import ContractStatusEventModel
from src.models.contract_model import ContractModel
from src.models.contract_status_model import ContractStatusModel

class ContractStatusEventRepository(EnumeratorRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        
    def create(self, contract: ContractModel, status: ContractStatusModel, user_data: dict) -> ContractStatusEventModel:
        event = ContractStatusEventModel(
            contract = contract,
            status=status,
            user_data=user_data
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete(self, event_model: ContractStatusEventModel) -> None:
        self.db.delete(event_model)
        self.db.commit()