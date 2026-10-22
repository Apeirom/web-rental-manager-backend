from decimal import Decimal, InvalidOperation

from src.constants.property_constants import (
    EQUITY_PARTICIPATION_MINIMUM_PERCENTAGE,
    EQUITY_PARTICIPATION_PERCENTAGE_BASE,
)
from src.repository.property_repository import PropertyRepository
from src.repository.owner_repository import OwnerRepository
from src.schemas.property_schema import (
    PropertyCreateSchema,
    PropertySchema,
    PropertyUpdateSchema,
)
from src.dto.property_dto import PropertyDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import (
    OwnerNotFoundError,
    PropertyEquityDuplicateOwnerError,
    PropertyEquityParticipationInvalidPercentageError,
    PropertyEquityParticipationRequiredError,
    PropertyEquityParticipationTotalExceededError,
    PropertyNotFoundError,
)

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
        require_participation: bool,
    ) -> list[tuple[int, Decimal]]:
        requested = schema.equity_participations
        if require_participation and not requested:
            raise PropertyEquityParticipationRequiredError()

        owner_keys: set[str] = set()
        total_percentage = Decimal("0")
        for item in requested:
            if item.owner_key in owner_keys:
                raise PropertyEquityDuplicateOwnerError(owner_key=item.owner_key)
            owner_keys.add(item.owner_key)

            percentage = item.participation_percentage
            valid_percentage = percentage.is_finite()
            if valid_percentage:
                try:
                    quantized_percentage = percentage.quantize(
                        EQUITY_PARTICIPATION_MINIMUM_PERCENTAGE
                    )
                except InvalidOperation:
                    valid_percentage = False
                else:
                    valid_percentage = (
                        EQUITY_PARTICIPATION_MINIMUM_PERCENTAGE
                        <= percentage
                        <= EQUITY_PARTICIPATION_PERCENTAGE_BASE
                        and quantized_percentage == percentage
                    )

            if not valid_percentage:
                raise PropertyEquityParticipationInvalidPercentageError(
                    owner_key=item.owner_key,
                    percentage=str(percentage),
                )
            total_percentage += percentage

        if total_percentage > EQUITY_PARTICIPATION_PERCENTAGE_BASE:
            raise PropertyEquityParticipationTotalExceededError(
                total_percentage=str(total_percentage),
            )

        participations = []
        for item in requested:
            owner_key = item.owner_key
            owner_model = self.owner_repository.get_by_key(owner_key)
            if not owner_model:
                raise OwnerNotFoundError(owner_key=owner_key)
            participations.append(
                (owner_model.id, item.participation_percentage)
            )
        return participations

    def create_property(self, schema: PropertyCreateSchema) -> PropertyDTO:
        participations = self._resolve_participations(
            schema,
            require_participation=True,
        )
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

        participations = self._resolve_participations(
            schema,
            require_participation=False,
        )
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