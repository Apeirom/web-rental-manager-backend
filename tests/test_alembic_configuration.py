import ast
from pathlib import Path

import src.models as models
from src.database.url import normalize_database_url
from src.models.base import Base

INITIAL_MIGRATION_PATH = (
    Path(__file__).parent.parent
    / "alembic"
    / "versions"
    / "84032990799d_initial_migration.py"
)
CURRENT_MIGRATION_PATH = (
    Path(__file__).parent.parent
    / "alembic"
    / "versions"
    / "7532217ba049_cleanup_old_tables.py"
)


def _migration_operations(function_name: str) -> list[ast.Call]:
    migration_tree = ast.parse(CURRENT_MIGRATION_PATH.read_text(encoding="utf-8"))
    function = next(
        node
        for node in migration_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    )
    return [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "op"
    ]


def _operation_arguments(
    operations: list[ast.Call],
    operation_name: str,
) -> list[list[str]]:
    matching_calls = [
        call
        for call in operations
        if isinstance(call.func, ast.Attribute)
        and call.func.attr == operation_name
    ]
    return [
        [ast.unparse(argument) for argument in call.args]
        for call in matching_calls
    ]


def test_normalize_database_url_converts_legacy_postgres_scheme():
    assert normalize_database_url("postgres://user:pass@localhost/db") == (
        "postgresql://user:pass@localhost/db"
    )


def test_normalize_database_url_preserves_other_schemes():
    database_url = "sqlite:///test.db"

    assert normalize_database_url(database_url) == database_url


def test_models_package_registers_all_tables_in_metadata():
    assert models.UserModel.__table__.metadata is Base.metadata
    assert set(Base.metadata.tables) == {
        "contract_status_events",
        "contracts",
        "extract_batches",
        "equity_participations",
        "contract_statuses",
        "extracts",
        "extract_item_categories",
        "extract_items",
        "owners",
        "payments",
        "real_estates",
        "guarantees",
        "guarantee_deposits",
        "guarantee_guarantors",
        "guarantee_bail_insurances",
        "properties",
        "tenants",
        "users",
    }


def test_initial_migration_preserves_confirmed_tables_and_columns():
    upgrade_operations = _migration_operations("upgrade")
    downgrade_operations = _migration_operations("downgrade")

    dropped_tables = {
        arguments[0].strip("'")
        for arguments in _operation_arguments(upgrade_operations, "drop_table")
    }
    assert dropped_tables == {"guarantors_old", "bail_insurances_old"}

    dropped_columns = {
        (arguments[0].strip("'"), arguments[1].strip("'"))
        for arguments in _operation_arguments(upgrade_operations, "drop_column")
    }
    assert ("properties", "owner_id") not in dropped_columns
    assert ("extract_item_categories", "description") not in dropped_columns

    created_tables_on_downgrade = {
        arguments[0].strip("'")
        for arguments in _operation_arguments(downgrade_operations, "create_table")
    }
    assert "guarantee_types" not in created_tables_on_downgrade


def test_initial_migration_has_named_foreign_keys_and_explicit_casts():
    upgrade_operations = _migration_operations("upgrade")
    downgrade_operations = _migration_operations("downgrade")

    created_foreign_keys = _operation_arguments(
        upgrade_operations,
        "create_foreign_key",
    )
    assert created_foreign_keys
    assert all(arguments[0] != "None" for arguments in created_foreign_keys)

    dropped_foreign_keys = _operation_arguments(
        downgrade_operations,
        "drop_constraint",
    )
    assert all(arguments[0] != "None" for arguments in dropped_foreign_keys)

    migration_source = CURRENT_MIGRATION_PATH.read_text(encoding="utf-8")
    assert 'postgresql_using="extract_batch_id::integer"' in migration_source
    assert 'postgresql_using="type::text::guaranteetypeenum"' in migration_source
    assert 'postgresql_using="type::text"' in migration_source


def test_cleanup_migration_follows_stamped_initial_revision():
    migration_tree = ast.parse(
        CURRENT_MIGRATION_PATH.read_text(encoding="utf-8")
    )
    initial_tree = ast.parse(
        INITIAL_MIGRATION_PATH.read_text(encoding="utf-8")
    )
    current_revision = next(
        node.value.value
        for node in migration_tree.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "revision"
    )
    current_parent = next(
        node.value.value
        for node in migration_tree.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "down_revision"
    )
    initial_revision = next(
        node.value.value
        for node in initial_tree.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "revision"
    )

    assert current_revision == "7532217ba049"
    assert current_parent == initial_revision == "84032990799d"
