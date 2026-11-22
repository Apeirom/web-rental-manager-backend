"""add_condominium_extract_item_category

Revision ID: 1d6798c4befa
Revises: 8d5f0c69acb2
Create Date: 2026-11-22 17:51:50.882495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = '1d6798c4befa'
down_revision: Union[str, None] = '8d5f0c69acb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    existing = connection.execute(
        sa.text("SELECT id FROM extract_item_categories WHERE enumerator = :enumerator"),
        {"enumerator": "condominium"},
    ).scalar_one_or_none()
    if existing is None:
        connection.execute(
            sa.text("INSERT INTO extract_item_categories (enumerator) VALUES (:enumerator)"),
            {"enumerator": "condominium"},
        )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM extract_item_categories WHERE enumerator = :enumerator"),
        {"enumerator": "condominium"},
    )
