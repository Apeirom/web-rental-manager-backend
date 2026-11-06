"""enable_row_level_security_on_all_tables

Revision ID: f610eeb383b2
Revises: 318614ac0ca0
Create Date: 2026-11-05 19:48:16.204641

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'f610eeb383b2'
down_revision: Union[str, None] = '318614ac0ca0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES: tuple[str, ...] = (
    "users",
    "real_estates",
    "tenants",
    "owners",
    "properties",
    "equity_participations",
    "contract_statuses",
    "guarantees",
    "guarantee_deposits",
    "guarantee_guarantors",
    "guarantee_bail_insurances",
    "contracts",
    "contract_status_events",
    "payments",
    "extract_batches",
    "extracts",
    "extract_item_categories",
    "extract_items",
    "alembic_version",
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for table in TABLES:
            op.execute(f"ALTER TABLE IF EXISTS {table} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for table in TABLES:
            op.execute(f"ALTER TABLE IF EXISTS {table} DISABLE ROW LEVEL SECURITY")
