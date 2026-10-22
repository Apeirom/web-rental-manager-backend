import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


MIGRATION_PATH = (
    Path(__file__).parent.parent
    / "alembic"
    / "versions"
    / "f8027ea5bc90_drop_legacy_property_owner_id.py"
)
MIGRATION_SPEC = importlib.util.spec_from_file_location(
    "drop_property_owner_id_migration",
    MIGRATION_PATH,
)
assert MIGRATION_SPEC is not None
assert MIGRATION_SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(MIGRATION_SPEC)
MIGRATION_SPEC.loader.exec_module(MIGRATION)


class _MigrationOperations:
    def __init__(self, connection):
        self.connection = connection
        self.operations = Operations(MigrationContext.configure(connection))

    def get_bind(self):
        return self.connection

    def drop_column(self, *args, **kwargs):
        return self.operations.drop_column(*args, **kwargs)

    def add_column(self, *args, **kwargs):
        return self.operations.add_column(*args, **kwargs)

    def alter_column(self, table_name, column_name, **kwargs):
        assert table_name == "properties"
        assert column_name == "owner_id"
        assert kwargs == {"nullable": False}


def _create_schema(connection):
    connection.exec_driver_sql(
        "CREATE TABLE properties ("
        "id INTEGER PRIMARY KEY, property_name TEXT NOT NULL, owner_id INTEGER)"
    )
    connection.exec_driver_sql(
        "CREATE TABLE owners (id INTEGER PRIMARY KEY)"
    )
    connection.exec_driver_sql(
        "CREATE TABLE equity_participations ("
        "property_id INTEGER NOT NULL, "
        "owner_id INTEGER NOT NULL, "
        "participation_percentage NUMERIC(5, 2) NOT NULL)"
    )
    connection.execute(
        text("INSERT INTO owners (id) VALUES (:id)"),
        [{"id": 1}, {"id": 2}, {"id": 3}],
    )
    connection.execute(
        text(
            "INSERT INTO properties (id, property_name, owner_id) "
            "VALUES (:id, :name, :owner_id)"
        ),
        [
            {"id": 1, "name": "Single owner one", "owner_id": 1},
            {"id": 2, "name": "Single owner two", "owner_id": 2},
            {"id": 4, "name": "75 Galpão", "owner_id": 3},
        ],
    )
    connection.execute(
        text(
            "INSERT INTO equity_participations "
            "(property_id, owner_id, participation_percentage) "
            "VALUES (:property_id, :owner_id, :percentage)"
        ),
        [
            {"property_id": 1, "owner_id": 1, "percentage": 100},
            {"property_id": 2, "owner_id": 2, "percentage": 100},
            {"property_id": 4, "owner_id": 1, "percentage": 50},
            {"property_id": 4, "owner_id": 2, "percentage": 50},
        ],
    )


def test_migration_upgrade_and_downgrade_roundtrip_known_ownership():
    engine = create_engine("sqlite://")
    original_operations = MIGRATION.op
    try:
        with engine.begin() as connection:
            _create_schema(connection)
            MIGRATION.op = _MigrationOperations(connection)

            MIGRATION.upgrade()

            assert "owner_id" not in {
                column["name"]
                for column in inspect(connection).get_columns("properties")
            }

            MIGRATION.downgrade()

            assert "owner_id" in {
                column["name"]
                for column in inspect(connection).get_columns("properties")
            }
            restored_owners = connection.execute(
                text("SELECT id, owner_id FROM properties ORDER BY id")
            ).all()

        assert restored_owners == [(1, 1), (2, 2), (4, 3)]
    finally:
        MIGRATION.op = original_operations
        engine.dispose()


def test_downgrade_mapping_rejects_unrepresentable_shared_ownership():
    rows = [
        (1, "Single owner", 1, Decimal("100.00")),
        (1, "Single owner", 2, Decimal("25.00")),
    ]

    with pytest.raises(RuntimeError, match="expected one owner with 100%"):
        MIGRATION._build_legacy_owner_mapping(rows)


def test_downgrade_mapping_rejects_changed_legacy_shared_property():
    rows = [
        (4, "Renamed property", 1, Decimal("50.00")),
        (4, "Renamed property", 2, Decimal("50.00")),
    ]

    with pytest.raises(RuntimeError, match="name or 50/50 ownership has changed"):
        MIGRATION._build_legacy_owner_mapping(rows)
