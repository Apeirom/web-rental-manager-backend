"""drop_legacy_property_owner_id

Revision ID: f8027ea5bc90
Revises: a2a47c90ef81
Create Date: 2026-10-22 00:20:07.055507

"""
from collections.abc import Sequence
from decimal import Decimal
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f8027ea5bc90'
down_revision: Union[str, None] = 'a2a47c90ef81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LEGACY_SHARED_PROPERTY_ID = 4
LEGACY_SHARED_PROPERTY_NAME = "75 Galpão"
LEGACY_SHARED_OWNER_ID = 3
LEGACY_SHARED_PARTICIPATIONS = (
    (1, Decimal("50.00")),
    (2, Decimal("50.00")),
)
FULL_PARTICIPATION_PERCENTAGE = Decimal("100.00")


def _build_legacy_owner_mapping(
    properties: Sequence[
        tuple[int, str, int | None, Decimal | None]
    ],
) -> dict[int, int]:
    participations_by_property: dict[
        int, tuple[str, list[tuple[int, Decimal]]]
    ] = {}
    for property_id, property_name, owner_id, percentage in properties:
        if property_id not in participations_by_property:
            participations_by_property[property_id] = (property_name, [])
        if owner_id is not None and percentage is not None:
            participations_by_property[property_id][1].append(
                (owner_id, Decimal(str(percentage)))
            )

    owner_mapping: dict[int, int] = {}
    for property_id, (property_name, participations) in (
        participations_by_property.items()
    ):
        if property_id == LEGACY_SHARED_PROPERTY_ID:
            if (
                property_name != LEGACY_SHARED_PROPERTY_NAME
                or tuple(sorted(participations))
                != LEGACY_SHARED_PARTICIPATIONS
            ):
                raise RuntimeError(
                    "Cannot restore legacy owner_id for property 4: "
                    "its name or 50/50 ownership has changed."
                )
            owner_mapping[property_id] = LEGACY_SHARED_OWNER_ID
            continue

        if (
            len(participations) != 1
            or participations[0][1] != FULL_PARTICIPATION_PERCENTAGE
        ):
            raise RuntimeError(
                "Cannot restore legacy owner_id for property "
                f"{property_id}: expected one owner with 100% participation."
            )
        owner_mapping[property_id] = participations[0][0]

    return owner_mapping


def _restore_legacy_owner_ids(connection: sa.Connection) -> None:
    property_rows = connection.execute(
        sa.text(
            "SELECT properties.id, properties.property_name, "
            "equity_participations.owner_id, "
            "equity_participations.participation_percentage "
            "FROM properties "
            "LEFT JOIN equity_participations "
            "ON equity_participations.property_id = properties.id "
            "ORDER BY properties.id, equity_participations.owner_id"
        )
    ).all()
    owner_mapping = _build_legacy_owner_mapping(property_rows)

    existing_owner_ids = set(
        connection.execute(sa.text("SELECT id FROM owners")).scalars()
    )
    missing_owner_ids = set(owner_mapping.values()) - existing_owner_ids
    if missing_owner_ids:
        raise RuntimeError(
            "Cannot restore legacy owner_id because owner IDs are missing: "
            f"{sorted(missing_owner_ids)}."
        )

    if owner_mapping:
        connection.execute(
            sa.text(
                "UPDATE properties SET owner_id = :owner_id WHERE id = :property_id"
            ),
            [
                {"property_id": property_id, "owner_id": owner_id}
                for property_id, owner_id in owner_mapping.items()
            ],
        )


def upgrade() -> None:
    op.drop_column("properties", "owner_id")


def downgrade() -> None:
    op.add_column(
        "properties",
        sa.Column("owner_id", sa.Integer(), nullable=True),
    )
    _restore_legacy_owner_ids(op.get_bind())
    op.alter_column("properties", "owner_id", nullable=False)
