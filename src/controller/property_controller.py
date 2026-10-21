from decimal import Decimal

from src.constants.property_constants import EQUITY_PARTICIPATION_PERCENTAGE_BASE
from src.repository.property_repository import PropertyRepository
from src.repository.owner_repository import OwnerRepository
from src.schemas.property_schema import (
    PropertyCreateSchema,
    PropertySchema,
    PropertyUpdateSchema,
)
from src.dto.property_dto import PropertyDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import PropertyNotFoundError, OwnerNotFoundError

class PropertyController:
    def __init__(
        self,
        property_repository: PropertyRepository,
        owner_repository: OwnerRepository,
    ):
        self.property_repository = property_repository
        self.owner_repository = owner_repository

    def _resolve_participations(
        self,
        schema: PropertySchema,
    ) -> list[tuple[int, Decimal]]:
        if schema.equity_participations:
            requested = [
                (item.owner_key, item.participation_percentage)
                for item in schema.equity_participations
            ]
        else:
            if schema.owner_key is None:
                raise ValueError("Informe ao menos uma participação de proprietário.")
            requested = [
                (schema.owner_key, EQUITY_PARTICIPATION_PERCENTAGE_BASE)
            ]

        participations = []
        for owner_key, percentage in requested:
            owner_model = self.owner_repository.get_by_key(owner_key)
            if not owner_model:
                raise OwnerNotFoundError(owner_key=owner_key)
            participations.append((owner_model.id, percentage))
        return participations

    def create_property(self, schema: PropertyCreateSchema) -> PropertyDTO:
        participations = self._resolve_participations(schema)
        property_model = self.property_repository.create(
            property_name=schema.property_name,
            participations=participations,
            address=schema.address,
            room_count=schema.room_count,
        )
        return PropertyDTO.model_validate(property_model)

    def get_property(self, property_key: str) -> PropertyDTO:
        property_model = self.property_repository.get_by_key(property_key)
        if not property_model:
            raise PropertyNotFoundError(property_key=property_key)
        return PropertyDTO.model_validate(property_model)

    def get_paginated_properties(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search_term: str | None = None,
        property_name: str | None = None,
        owner_name: str | None = None,
        only_active_contracts: bool = False
    ) -> PaginatedResponseDTO[PropertyDTO]:
        
        total_count, property_models = self.property_repository.get_paginated(
            skip=skip, 
            limit=limit, 
            search_term=search_term,
            property_name=property_name,
            owner_name=owner_name,
            only_active_contracts=only_active_contracts
        )
        
        property_dtos = [PropertyDTO.model_validate(p) for p in property_models]
        
        return PaginatedResponseDTO(
            total=total_count,
            skip=skip,
            limit=limit,
            data=property_dtos
        )

    def update_property(self, property_key: str, schema: PropertyUpdateSchema) -> PropertyDTO:
        property_model = self.property_repository.get_by_key(
            property_key, for_update=True
        )
        if not property_model:
            raise PropertyNotFoundError(property_key=property_key)

        participations = self._resolve_participations(schema)
        updated_model = self.property_repository.update(
            property_model=property_model,
            property_name=schema.property_name,
            participations=participations,
            address=schema.address,
            room_count=schema.room_count,
        )
        return PropertyDTO.model_validate(updated_model)

    def delete_property(self, property_key: str) -> None:
        property_model = self.property_repository.get_by_key(property_key)
        if not property_model:
            raise PropertyNotFoundError(property_key=property_key)
        self.property_repository.delete(property_model)