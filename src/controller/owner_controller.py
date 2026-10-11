from sqlalchemy.orm import Session
from src.models.contract_model import ContractModel
from src.models.extract_batch_model import ExtractBatchModel
from src.models.extract_model import ExtractModel
from src.repository.owner_repository import OwnerRepository
from src.schemas.owner_schema import OwnerCreateSchema, OwnerUpdateSchema
from src.dto.owner_dto import OwnerDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import OwnerNotFoundError

class OwnerController:
    def __init__(self, db: Session):
        self.db = db
        self.owner_repository = OwnerRepository(db)

    def create_owner(self, schema: OwnerCreateSchema) -> OwnerDTO:
        owner_model = self.owner_repository.create(
            name=schema.name,
            document_number=schema.document_number
        )
        return OwnerDTO.model_validate(owner_model)

    def get_owner(self, owner_key: str) -> OwnerDTO:
        owner_model = self.owner_repository.get_by_key(owner_key)
        if not owner_model:
            raise OwnerNotFoundError(owner_key=owner_key)
        return OwnerDTO.model_validate(owner_model)

    def get_paginated_owners(self, skip: int = 0, limit: int = 10, search_term: str = None) -> PaginatedResponseDTO[OwnerDTO]:
        total_count, owner_models = self.owner_repository.get_paginated(skip, limit, search_term)
        owner_dtos = [OwnerDTO.model_validate(o) for o in owner_models]
        return PaginatedResponseDTO(total=total_count, skip=skip, limit=limit, data=owner_dtos)

    def update_owner(self, owner_key: str, schema: OwnerUpdateSchema) -> OwnerDTO:
        owner_model = self.owner_repository.get_by_key(owner_key)
        if not owner_model:
            raise OwnerNotFoundError(owner_key=owner_key)
            
        updated_model = self.owner_repository.update(
            owner_model=owner_model,
            name=schema.name,
            document_number=schema.document_number
        )
        return OwnerDTO.model_validate(updated_model)

    def delete_owner(self, owner_key: str) -> None:
        owner_model = self.owner_repository.get_by_key(owner_key)
        if not owner_model:
            raise OwnerNotFoundError(owner_key=owner_key)

        property_ids = [property_model.id for property_model in owner_model.properties]
        contracts = (
            self.db.query(ContractModel)
            .filter(ContractModel.property_id.in_(property_ids))
            .all()
            if property_ids
            else []
        )
        contract_ids = [contract.id for contract in contracts]

        if contract_ids:
            affected_extracts = (
                self.db.query(ExtractModel)
                .filter(ExtractModel.contract_id.in_(contract_ids))
                .all()
            )
            batch_ids = {extract.extract_batch_id for extract in affected_extracts}
            batches = (
                self.db.query(ExtractBatchModel)
                .filter(ExtractBatchModel.id.in_(batch_ids))
                .all()
                if batch_ids
                else []
            )

            for extract in affected_extracts:
                self.db.delete(extract)
            self.db.flush()

            for batch in batches:
                batch.payment_id = None
                remaining_extracts = (
                    self.db.query(ExtractModel)
                    .filter(ExtractModel.extract_batch_id == batch.id)
                    .all()
                )
                if remaining_extracts:
                    batch.total_net_transfer = round(
                        sum(extract.net_transfer for extract in remaining_extracts),
                        2,
                    )
                else:
                    self.db.delete(batch)

            for contract in contracts:
                self.db.delete(contract)
            self.db.flush()

        self.owner_repository.delete(owner_model)