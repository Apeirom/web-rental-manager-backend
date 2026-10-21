"""migrate_legacy_property_ownership

Revision ID: a2a47c90ef81
Revises: 7532217ba049
Create Date: 2026-10-21 03:06:41.900578

"""
from collections.abc import Sequence
from decimal import Decimal
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a2a47c90ef81'
down_revision: Union[str, None] = '7532217ba049'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LEGACY_OWNER_PARTICIPATIONS = {
    1: ((1, Decimal("100.00")),),
    2: ((2, Decimal("100.00")),),
    3: ((1, Decimal("50.00")), (2, Decimal("50.00"))),
}


def _build_equity_participation_rows(
    properties: Sequence[tuple[int, int]],
) -> list[dict[str, int | Decimal]]:
    rows: list[dict[str, int | Decimal]] = []
    for property_id, legacy_owner_id in properties:
        for owner_id, percentage in LEGACY_OWNER_PARTICIPATIONS[legacy_owner_id]:
            rows.append(
                {
                    "property_id": property_id,
                    "owner_id": owner_id,
                    "participation_percentage": percentage,
                }
            )
    return rows


def _get_legacy_properties(connection: sa.Connection) -> list[tuple[int, int]]:
    owner_ids = tuple(LEGACY_OWNER_PARTICIPATIONS)
    query = sa.text(
        "SELECT id, owner_id FROM properties "
        "WHERE owner_id IN :owner_ids ORDER BY id"
    ).bindparams(sa.bindparam("owner_ids", expanding=True))
    properties = connection.execute(query, {"owner_ids": owner_ids}).all()
    return [(int(property_id), int(owner_id)) for property_id, owner_id in properties]


def _upgrade(connection: sa.Connection) -> None:
    rows = _build_equity_participation_rows(_get_legacy_properties(connection))
    if not rows:
        return

    property_ids = tuple({int(row["property_id"]) for row in rows})
    existing_query = sa.text(
        "SELECT property_id FROM equity_participations "
        "WHERE property_id IN :property_ids LIMIT 1"
    ).bindparams(sa.bindparam("property_ids", expanding=True))
    existing_property_id = connection.execute(
        existing_query,
        {"property_ids": property_ids},
    ).scalar_one_or_none()
    if existing_property_id is not None:
        raise RuntimeError(
            "Cannot migrate legacy property ownership because "
            f"property {existing_property_id} already has equity participations."
        )

    owner_ids = tuple({int(row["owner_id"]) for row in rows})
    owners_query = sa.text(
        "SELECT id FROM owners WHERE id IN :owner_ids"
    ).bindparams(sa.bindparam("owner_ids", expanding=True))
    existing_owner_ids = set(
        connection.execute(owners_query, {"owner_ids": owner_ids}).scalars()
    )
    missing_owner_ids = set(owner_ids) - existing_owner_ids
    if missing_owner_ids:
        raise RuntimeError(
            "Cannot migrate legacy property ownership because required owner "
            f"IDs are missing: {sorted(missing_owner_ids)}."
        )

    insert_query = sa.text(
        "INSERT INTO equity_participations "
        "(property_id, owner_id, participation_percentage) "
        "VALUES (:property_id, :owner_id, :participation_percentage)"
    ).bindparams(
        sa.bindparam("participation_percentage", type_=sa.Numeric(5, 2))
    )
    connection.execute(insert_query, rows)


def _downgrade(connection: sa.Connection) -> None:
    rows = _build_equity_participation_rows(_get_legacy_properties(connection))
    if not rows:
        return

    delete_query = sa.text(
        "DELETE FROM equity_participations "
        "WHERE property_id = :property_id "
        "AND owner_id = :owner_id "
        "AND participation_percentage = :participation_percentage"
    ).bindparams(
        sa.bindparam("participation_percentage", type_=sa.Numeric(5, 2))
    )
    connection.execute(delete_query, rows)


def upgrade() -> None:
    _upgrade(op.get_bind())


def downgrade() -> None:
    _downgrade(op.get_bind())
