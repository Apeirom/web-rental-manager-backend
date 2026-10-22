"""cleanup_old_tables

Revision ID: 7532217ba049
Revises: 84032990799d
Create Date: 2026-10-21 02:44:20.010623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "7532217ba049"
down_revision: Union[str, None] = "84032990799d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f("ix_bail_insurances_id"), table_name="bail_insurances_old")
    op.drop_index(op.f("ix_bail_insurances_key"), table_name="bail_insurances_old")
    op.drop_table("bail_insurances_old")
    op.drop_index(op.f("ix_guarantors_id"), table_name="guarantors_old")
    op.drop_index(op.f("ix_guarantors_key"), table_name="guarantors_old")
    op.drop_table("guarantors_old")

    op.alter_column(
        "contracts",
        "guarantee_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.drop_constraint(
        op.f("contracts_guarantee_id_fkey"),
        "contracts",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("contracts_real_estate_id_fkey"),
        "contracts",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("contracts_tenant_id_fkey"),
        "contracts",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("contracts_property_id_fkey"),
        "contracts",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("contracts_real_estate_id_fkey"),
        "contracts",
        "real_estates",
        ["real_estate_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("contracts_tenant_id_fkey"),
        "contracts",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("contracts_guarantee_id_fkey"),
        "contracts",
        "guarantees",
        ["guarantee_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("contracts_property_id_fkey"),
        "contracts",
        "properties",
        ["property_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        op.f("extract_batches_payment_id_fkey"),
        "extract_batches",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("extract_batches_payment_id_fkey"),
        "extract_batches",
        "payments",
        ["payment_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_constraint(
        op.f("extract_items_extract_id_fkey"),
        "extract_items",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("extract_items_extract_id_fkey"),
        "extract_items",
        "extracts",
        ["extract_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.alter_column(
        "extracts",
        "extract_batch_id",
        existing_type=sa.NUMERIC(),
        type_=sa.Integer(),
        nullable=False,
        postgresql_using="extract_batch_id::integer",
    )
    op.drop_constraint(
        op.f("extracts_contract_id_fkey"),
        "extracts",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("extracts_extract_batch_id_fkey"),
        "extracts",
        "extract_batches",
        ["extract_batch_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("extracts_contract_id_fkey"),
        "extracts",
        "contracts",
        ["contract_id"],
        ["id"],
        ondelete="CASCADE",
    )

    guarantee_type = postgresql.ENUM(
        "DEPOSIT",
        "GUARANTOR",
        "BAIL_INSURANCE",
        "BASE",
        name="guaranteetypeenum",
    )
    guarantee_type.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "guarantees",
        "type",
        existing_type=sa.VARCHAR(length=50),
        type_=postgresql.ENUM(
            "DEPOSIT",
            "GUARANTOR",
            "BAIL_INSURANCE",
            "BASE",
            name="guaranteetypeenum",
            create_type=False,
        ),
        existing_nullable=False,
        postgresql_using="type::text::guaranteetypeenum",
    )


def downgrade() -> None:
    op.alter_column(
        "guarantees",
        "type",
        existing_type=postgresql.ENUM(
            "DEPOSIT",
            "GUARANTOR",
            "BAIL_INSURANCE",
            "BASE",
            name="guaranteetypeenum",
            create_type=False,
        ),
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
        postgresql_using="type::text",
    )

    op.drop_constraint(
        op.f("extracts_contract_id_fkey"),
        "extracts",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("extracts_extract_batch_id_fkey"),
        "extracts",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("extracts_contract_id_fkey"),
        "extracts",
        "contracts",
        ["contract_id"],
        ["id"],
    )
    op.alter_column(
        "extracts",
        "extract_batch_id",
        existing_type=sa.Integer(),
        type_=sa.NUMERIC(),
        nullable=True,
        postgresql_using="extract_batch_id::numeric",
    )

    op.drop_constraint(
        op.f("extract_items_extract_id_fkey"),
        "extract_items",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("extract_items_extract_id_fkey"),
        "extract_items",
        "extracts",
        ["extract_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("extract_batches_payment_id_fkey"),
        "extract_batches",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("extract_batches_payment_id_fkey"),
        "extract_batches",
        "payments",
        ["payment_id"],
        ["id"],
    )

    op.drop_constraint(
        op.f("contracts_guarantee_id_fkey"),
        "contracts",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("contracts_tenant_id_fkey"),
        "contracts",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("contracts_real_estate_id_fkey"),
        "contracts",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("contracts_property_id_fkey"),
        "contracts",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("contracts_guarantee_id_fkey"),
        "contracts",
        "guarantees",
        ["guarantee_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("contracts_tenant_id_fkey"),
        "contracts",
        "tenants",
        ["tenant_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("contracts_real_estate_id_fkey"),
        "contracts",
        "real_estates",
        ["real_estate_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("contracts_property_id_fkey"),
        "contracts",
        "properties",
        ["property_id"],
        ["id"],
    )
    op.alter_column(
        "contracts",
        "guarantee_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )

    op.create_table(
        "guarantors_old",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("key", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "document_number",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("guarantors_pkey")),
        sa.UniqueConstraint(
            "document_number",
            name=op.f("guarantors_document_number_key"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )
    op.create_index(
        op.f("ix_guarantors_key"),
        "guarantors_old",
        ["key"],
        unique=True,
    )
    op.create_index(
        op.f("ix_guarantors_id"),
        "guarantors_old",
        ["id"],
        unique=False,
    )
    op.create_table(
        "bail_insurances_old",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("key", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "value",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("validity", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "insurance_company",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("bail_insurances_pkey")),
    )
    op.create_index(
        op.f("ix_bail_insurances_key"),
        "bail_insurances_old",
        ["key"],
        unique=True,
    )
    op.create_index(
        op.f("ix_bail_insurances_id"),
        "bail_insurances_old",
        ["id"],
        unique=False,
    )
