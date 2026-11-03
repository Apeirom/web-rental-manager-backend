import importlib.util
from pathlib import Path
from src.models import ContractModel, ExtractModel, PaymentModel

MIGRATION_PATH = (
    Path(__file__).parent.parent
    / "alembic"
    / "versions"
    / "318614ac0ca0_add_indexes_for_contracts_extracts_.py"
)
MIGRATION_SPEC = importlib.util.spec_from_file_location(
    "add_indexes_for_contracts_extracts_payments_migration",
    MIGRATION_PATH,
)
assert MIGRATION_SPEC is not None
assert MIGRATION_SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(MIGRATION_SPEC)
MIGRATION_SPEC.loader.exec_module(MIGRATION)


def test_migration_chain():
    assert MIGRATION.revision == "318614ac0ca0"
    assert MIGRATION.down_revision == "f8027ea5bc90"


def test_models_have_expected_indexes():
    contract_indexed_columns = {
        col.name for col in ContractModel.__table__.columns if col.index
    }
    assert "property_id" in contract_indexed_columns
    assert "tenant_id" in contract_indexed_columns
    assert "real_estate_id" in contract_indexed_columns
    assert "status_id" in contract_indexed_columns
    assert "guarantee_id" in contract_indexed_columns

    extract_indexed_columns = {
        col.name for col in ExtractModel.__table__.columns if col.index
    }
    assert "extract_batch_id" in extract_indexed_columns
    assert "contract_id" in extract_indexed_columns

    extract_indexes = {idx.name: [c.name for c in idx.columns] for idx in ExtractModel.__table__.indexes}
    assert "ix_extracts_contract_ref" in extract_indexes
    assert extract_indexes["ix_extracts_contract_ref"] == ["contract_id", "month_ref", "year_ref"]

    payment_indexed_columns = {
        col.name for col in PaymentModel.__table__.columns if col.index
    }
    assert "payment_date" in payment_indexed_columns
    assert "amount" in payment_indexed_columns

