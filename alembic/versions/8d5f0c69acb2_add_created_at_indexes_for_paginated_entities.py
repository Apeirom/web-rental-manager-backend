"""add_created_at_indexes_for_paginated_entities

Revision ID: 8d5f0c69acb2
Revises: e39b7c8e2101
Create Date: 2026-11-07 13:06:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '8d5f0c69acb2'
down_revision: Union[str, None] = 'e39b7c8e2101'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f('ix_contracts_created_at'), 'contracts', ['created_at'], unique=False)
    op.create_index(op.f('ix_extract_batches_created_at'), 'extract_batches', ['created_at'], unique=False)
    op.create_index(op.f('ix_guarantees_created_at'), 'guarantees', ['created_at'], unique=False)
    op.create_index(op.f('ix_owners_created_at'), 'owners', ['created_at'], unique=False)
    op.create_index(op.f('ix_properties_created_at'), 'properties', ['created_at'], unique=False)
    op.create_index(op.f('ix_real_estates_created_at'), 'real_estates', ['created_at'], unique=False)
    op.create_index(op.f('ix_tenants_created_at'), 'tenants', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_index(op.f('ix_tenants_created_at'), table_name='tenants')
    op.drop_index(op.f('ix_real_estates_created_at'), table_name='real_estates')
    op.drop_index(op.f('ix_properties_created_at'), table_name='properties')
    op.drop_index(op.f('ix_owners_created_at'), table_name='owners')
    op.drop_index(op.f('ix_guarantees_created_at'), table_name='guarantees')
    op.drop_index(op.f('ix_extract_batches_created_at'), table_name='extract_batches')
    op.drop_index(op.f('ix_contracts_created_at'), table_name='contracts')
