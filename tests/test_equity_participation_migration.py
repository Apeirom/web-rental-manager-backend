import importlib.util
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text


MIGRATION_PATH = (
    Path(__file__).parent.parent
    / "alembic"
    / "versions"
    / "a2a47c90ef81_migrate_legacy_property_ownership.py"
)
MIGRATION_SPEC = importlib.util.spec_from_file_location(
    "legacy_property_ownership_migration",
    MIGRATION_PATH,
)
assert MIGRATION_SPEC is not None
assert MIGRATION_SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(MIGRATION_SPEC)
MIGRATION_SPEC.loader.exec_module(MIGRATION)


def _create_legacy_schema(connection):
    connection.exec_driver_sql(
        "CREATE TABLE properties (id INTEGER PRIMARY KEY, owner_id INTEGER)"
    )
    connection.exec_driver_sql(
        "CREATE TABLE owners (id INTEGER PRIMARY KEY)"
    )
    connection.exec_driver_sql(
        "CREATE TABLE equity_participations ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "property_id INTEGER NOT NULL, "
        "owner_id INTEGER NOT NULL, "
        "participation_percentage NUMERIC NOT NULL, "
        "UNIQUE (property_id, owner_id))"
    )
    connection.execute(
        text("INSERT INTO owners (id) VALUES (:id)"),
        [{"id": 1}, {"id": 2}, {"id": 3}],
    )
    connection.execute(
        text("INSERT INTO properties (id, owner_id) VALUES (:id, :owner_id)"),
        [
            {"id": 10, "owner_id": 1},
            {"id": 20, "owner_id": 2},
            {"id": 30, "owner_id": 3},
            {"id": 40, "owner_id": None},
            {"id": 50, "owner_id": 4},
        ],
    )


def test_upgrade_migrates_each_legacy_owner_to_expected_participations():
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            _create_legacy_schema(connection)

            MIGRATION._upgrade(connection)

            rows = connection.execute(
                text(
                    "SELECT property_id, owner_id, participation_percentage "
                    "FROM equity_participations "
                    "ORDER BY property_id, owner_id"
                )
            ).all()

        assert rows == [
            (10, 1, 100),
            (20, 2, 100),
            (30, 1, 50),
            (30, 2, 50),
        ]
    finally:
        engine.dispose()


def test_upgrade_aborts_if_eligible_property_already_has_participations():
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            _create_legacy_schema(connection)
            connection.execute(
                text(
                    "INSERT INTO equity_participations "
                    "(property_id, owner_id, participation_percentage) "
                    "VALUES (10, 1, 100)"
                )
            )

            with pytest.raises(RuntimeError, match="already has equity participations"):
                MIGRATION._upgrade(connection)

            count = connection.execute(
                text("SELECT count(*) FROM equity_participations")
            ).scalar_one()

        assert count == 1
    finally:
        engine.dispose()


def test_downgrade_removes_only_the_migrated_participations():
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            _create_legacy_schema(connection)
            MIGRATION._upgrade(connection)

            MIGRATION._downgrade(connection)

            count = connection.execute(
                text("SELECT count(*) FROM equity_participations")
            ).scalar_one()

        assert count == 0
    finally:
        engine.dispose()
