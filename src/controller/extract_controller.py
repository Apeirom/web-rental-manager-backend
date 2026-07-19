from sqlalchemy.orm import Session
from src.repository.extract_repository import ExtractRepository
from src.repository.extract_batch_repository import ExtractBatchRepository
from src.dto.extract_dto import ExtractDTO
from src.errors.custom_errors import ExtractNotFoundError

class ExtractController:
    def __init__(self, db: Session):
        self.extract_repository = ExtractRepository(db)
        self.extract_batch_repository = ExtractBatchRepository(db)

    def get_extract(self, batch_key: str, extract_key: str) -> ExtractDTO:
        extract_model = self.extract_repository.get_by_key(extract_key)
        if not extract_model or extract_model.batch.key != batch_key:
            raise ExtractNotFoundError(extract_key)
        return ExtractDTO.model_validate(extract_model)

    def delete_extract(self, batch_key: str, extract_key: str) -> None:
        batch_model = self.extract_batch_repository.get_by_key(batch_key)
        extract_model = self.extract_repository.get_by_key(extract_key)
        
        if not batch_model or not extract_model or extract_model.extract_batch_id != batch_model.id:
            raise ExtractNotFoundError(extract_key)

        self.extract_batch_repository.unlink_payment(batch_model)
        self.extract_repository.delete(extract_model)
        self.extract_batch_repository.recalculate_and_check_payment(batch_model)
        self.extract_batch_repository.commit()