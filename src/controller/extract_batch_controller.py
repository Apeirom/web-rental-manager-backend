from sqlalchemy.orm import Session
from src.repository.extract_batch_repository import ExtractBatchRepository
from src.repository.extract_repository import ExtractRepository
from src.repository.extract_item_repository import ExtractItemRepository
from src.repository.contract_repository import ContractRepository
from src.repository.payment_repository import PaymentRepository
from src.models import ExtractItemModel, ExtractItemCategoryModel
from src.schemas.extract_batch_schema import ExtractBatchCreateSchema, ExtractBatchUpdateSchema
from src.dto.extract_batch_dto import ExtractBatchDTO
from src.dto.payment_dto import PaymentReconciliationDTO, PaymentDTO
from src.dto.paginated_response import PaginatedResponseDTO
from src.errors.custom_errors import ExtractNotFoundError, ExtractInvalidRelationError, ExtractBatchNotFoundError
from src.connectors.S3_storage_connector import S3StorageConnector
from src.utils.file_handler import verify_file_path

class ExtractBatchController:
    def __init__(self, db: Session):
        self.extract_batch_repository = ExtractBatchRepository(db)
        self.extract_repository = ExtractRepository(db)
        self.extract_item_repository = ExtractItemRepository(db)
        self.contract_repository = ContractRepository(db)
        self.payment_repository = PaymentRepository(db)
        self.S3_connector = S3StorageConnector(bucket_name="extracts")

    def _calculate_net_transfer(self, items_schema) -> float:
        net_transfer = 0.0
        for item in items_schema:
            if not item.is_withheld_at_source:
                net_transfer += item.amount
            else:
                net_transfer -= item.amount
        return round(net_transfer, 2)

    def _create_extract_with_items(self, extract_schema, batch_id: int) -> float:
        contract_model = self.contract_repository.get_by_key(extract_schema.contract_key)
        if not contract_model:
            raise ExtractInvalidRelationError(entity_name="Contract", key=extract_schema.contract_key)
        
        net_transfer = self._calculate_net_transfer(extract_schema.items)
        
        extract_model = self.extract_repository.create(
            month_ref=extract_schema.month_ref, 
            year_ref=extract_schema.year_ref, 
            net_transfer=net_transfer,
            extract_batch_id=batch_id, 
            contract_id=contract_model.id
        )

        for item in extract_schema.items:
            category_model = self.extract_item_repository.get_enumerator_model(
                ExtractItemCategoryModel, item.category
            )
            
            self.extract_item_repository.create(
                extract_id=extract_model.id,
                category_id=category_model.id, 
                description=item.description,
                amount=item.amount,
                is_credit=item.is_credit,
                is_withheld_at_source=item.is_withheld_at_source
            )
            
        return net_transfer

    def create_batch(self, schema: ExtractBatchCreateSchema) -> ExtractBatchDTO:
        batch_model = self.extract_batch_repository.create(total_net_transfer=0.0, file_path=schema.file_path)
        
        total_net_transfer = 0.0
        for extract_schema in schema.extracts:
            net_transfer = self._create_extract_with_items(extract_schema, batch_model.id)
            total_net_transfer += net_transfer
            
        self.extract_batch_repository.update_total(batch_model, round(total_net_transfer, 2))
        self.extract_batch_repository.commit()
        return ExtractBatchDTO.model_validate(batch_model)

    def update_batch(self, batch_key: str, schema: ExtractBatchUpdateSchema) -> ExtractBatchDTO:
        batch_model = self.extract_batch_repository.get_by_key(batch_key)
        if not batch_model:
            raise ExtractBatchNotFoundError(batch_key)

        if verify_file_path(schema.file_path):
            batch_model.file_path = schema.file_path
        else:
            if schema.file_path == "":
                batch_model.file_path = None

        payload_updates = {}
        payload_adds = []

        for item in schema.extracts:
            if item.key:
                payload_updates[item.key] = item
            else:
                payload_adds.append(item)

        existing_extracts = {}
        for ext in batch_model.extracts:
            existing_extracts[ext.key] = ext

        total_net_transfer = 0.0
        total_net_transfer += self._process_existing_extracts(existing_extracts, payload_updates)
        total_net_transfer += self._process_new_extracts(payload_adds, batch_model.id)

        self.extract_batch_repository.update_total(batch_model, round(total_net_transfer, 2))
        self.extract_batch_repository.commit()
        self.extract_batch_repository.refresh(batch_model)

        return ExtractBatchDTO.model_validate(batch_model)

    def _process_existing_extracts(self, existing_extracts: dict, payload_updates: dict) -> float:
        total_net = 0.0

        for ext_key, ext_model in existing_extracts.items():
            if ext_key not in payload_updates:
                self.extract_repository.delete(ext_model)
            else:
                extract_schema = payload_updates[ext_key]
                contract = self.contract_repository.get_by_key(extract_schema.contract_key)
                
                net_transfer = self._calculate_net_transfer(extract_schema.items)
                total_net += net_transfer
                
                self.extract_repository.update(
                    extract_model=ext_model,
                    month_ref=extract_schema.month_ref,
                    year_ref=extract_schema.year_ref,
                    net_transfer=net_transfer,
                    contract_id=contract.id
                )

                existing_items = {}
                for item_model in ext_model.items:
                    existing_items[item_model.key] = item_model

                item_updates = {}
                item_adds = []
                for item_schema in extract_schema.items:
                    if getattr(item_schema, 'key', None):
                        item_updates[item_schema.key] = item_schema
                    else:
                        item_adds.append(item_schema)

                for item_key, item_model in existing_items.items():
                    if item_key not in item_updates:
                        self.extract_item_repository.delete(item_model)
                    else:
                        item_schema = item_updates[item_key]
                        category_model = self.extract_item_repository.get_enumerator_model(
                            ExtractItemCategoryModel, item_schema.category
                        )
                        self.extract_item_repository.update(
                            item_model=item_model,
                            category_id=category_model.id,
                            description=item_schema.description,
                            amount=item_schema.amount,
                            is_credit=item_schema.is_credit,
                            is_withheld_at_source=item_schema.is_withheld_at_source
                        )

                for item_schema in item_adds:
                    category_model = self.extract_item_repository.get_enumerator_model(
                        ExtractItemCategoryModel, item_schema.category
                    )
                    self.extract_item_repository.create(
                        extract_id=ext_model.id,
                        category_id=category_model.id,
                        description=item_schema.description,
                        amount=item_schema.amount,
                        is_credit=item_schema.is_credit,
                        is_withheld_at_source=item_schema.is_withheld_at_source
                    )
                
        return total_net

    def _process_new_extracts(self, payload_adds: list, batch_id: int) -> float:
        total_net = 0.0

        for extract_schema in payload_adds:
            net_transfer = self._create_extract_with_items(extract_schema, batch_id)
            total_net += net_transfer
            
        return total_net

    def delete_batch(self, batch_key: str) -> None:
        batch_model = self.extract_batch_repository.get_by_key(batch_key)
        if not batch_model:
            raise ExtractBatchNotFoundError(batch_key)
        
        self.extract_batch_repository.unlink_payment(batch_model)
        self.extract_batch_repository.delete(batch_model)
        self.extract_batch_repository.commit()

    def get_paginated_batches(self, skip: int, limit: int, search_term: str = None, only_active: bool = False, is_reconciled: bool = None) -> PaginatedResponseDTO[ExtractBatchDTO]:
        total, batch_models = self.extract_batch_repository.get_paginated(skip, limit, search_term, only_active, is_reconciled)
        
        extract_dtos = []
        for batch in batch_models:
            dto = ExtractBatchDTO.model_validate(batch)
            if dto.file_path:
                dto.file_path = self.S3_connector.get_signed_url(dto.file_path)
            extract_dtos.append(dto)
            
        return PaginatedResponseDTO(total=total, skip=skip, limit=limit, data=extract_dtos)

    def upload_receipt(self, batch_key: str, file_bytes: bytes, content_type: str) -> ExtractBatchDTO:
        batch_model = self.extract_batch_repository.get_by_key(batch_key)
        if not batch_model:
            raise ExtractBatchNotFoundError(batch_key)
        
        extension = ".pdf" if "pdf" in content_type else ""
        file_url = self.S3_connector.upload_file(file_bytes, f"{batch_key}_v1{extension}", content_type)
        batch_model.file_path = file_url
        self.extract_batch_repository.commit()
        return ExtractBatchDTO.model_validate(batch_model)
        
    def reconcile_batch(self, batch_key: str) -> PaymentReconciliationDTO:
        batch = self.extract_batch_repository.get_by_key(batch_key)
        if not batch: 
            raise ExtractBatchNotFoundError(batch_key)

        if batch.payment_id:
            already_linked_dto = PaymentDTO.model_validate(batch.payment)
            return PaymentReconciliationDTO(status="alreadyLinked", message="Lote já vinculado.", candidates=[already_linked_dto])

        count_itens, candidates = self.payment_repository.get_paginated(skip=0, limit=50, amount=batch.total_net_transfer, is_linked=False)
        
        candidate_dtos = []
        for p in candidates:
            candidate_dtos.append(PaymentDTO.model_validate(p))

        return PaymentReconciliationDTO(status="success", message=f"Encontrados {count_itens} pagamentos.", candidates=candidate_dtos)