"""drop_legacy_guarantee_types_table

Revision ID: e39b7c8e2101
Revises: f610eeb383b2
Create Date: 2026-11-06 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e39b7c8e2101'
down_revision: Union[str, None] = 'f610eeb383b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TABLE IF EXISTS guarantee_types CASCADE")
    else:
        op.execute("DROP TABLE IF EXISTS guarantee_types")


def downgrade() -> None:
    op.create_table(
        'guarantee_types',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('enumerator', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('guarantee_types_pkey')),
        sa.UniqueConstraint('enumerator', name=op.f('guarantee_types_enumerator_key')),
    )
