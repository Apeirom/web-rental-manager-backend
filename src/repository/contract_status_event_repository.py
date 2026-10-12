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

    def get_by_contract_ids(
        self,
        contract_ids: set[int],
    ) -> list[ContractStatusEventModel]:
        if not contract_ids:
            return []
        return (
            self.db.query(ContractStatusEventModel)
            .filter(ContractStatusEventModel.contract_id.in_(contract_ids))
            .all()
        )

    def delete(self, event_model: ContractStatusEventModel) -> None:
        self.db.delete(event_model)
        self.db.flush()

    def delete_many(self, events: list[ContractStatusEventModel]) -> None:
        for event in events:
            self.db.delete(event)
        self.db.flush()

    def delete_by_contract_ids(self, contract_ids: set[int]) -> None:
        events = self.get_by_contract_ids(contract_ids)
        self.delete_many(events)