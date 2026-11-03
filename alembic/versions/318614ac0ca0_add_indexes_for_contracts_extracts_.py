"""add_indexes_for_contracts_extracts_payments

Revision ID: 318614ac0ca0
Revises: f8027ea5bc90
Create Date: 2026-11-02 23:27:03.379744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '318614ac0ca0'
down_revision: Union[str, None] = 'f8027ea5bc90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f('ix_contracts_property_id'), 'contracts', ['property_id'], unique=False)
    op.create_index(op.f('ix_contracts_tenant_id'), 'contracts', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_contracts_real_estate_id'), 'contracts', ['real_estate_id'], unique=False)
    op.create_index(op.f('ix_contracts_status_id'), 'contracts', ['status_id'], unique=False)
    op.create_index(op.f('ix_contracts_guarantee_id'), 'contracts', ['guarantee_id'], unique=False)

    op.create_index(op.f('ix_extracts_extract_batch_id'), 'extracts', ['extract_batch_id'], unique=False)
    op.create_index(op.f('ix_extracts_contract_id'), 'extracts', ['contract_id'], unique=False)
    op.create_index('ix_extracts_contract_ref', 'extracts', ['contract_id', 'month_ref', 'year_ref'], unique=False)

    op.create_index(op.f('ix_payments_payment_date'), 'payments', ['payment_date'], unique=False)
    op.create_index(op.f('ix_payments_amount'), 'payments', ['amount'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_payments_amount'), table_name='payments')
    op.drop_index(op.f('ix_payments_payment_date'), table_name='payments')

    op.drop_index('ix_extracts_contract_ref', table_name='extracts')
    op.drop_index(op.f('ix_extracts_contract_id'), table_name='extracts')
    op.drop_index(op.f('ix_extracts_extract_batch_id'), table_name='extracts')

    op.drop_index(op.f('ix_contracts_guarantee_id'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_status_id'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_real_estate_id'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_tenant_id'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_property_id'), table_name='contracts')
