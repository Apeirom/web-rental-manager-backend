from decimal import Decimal
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.constants.income_tax_constants import IncomeTaxTenantType
from src.errors.custom_errors import (
    IncomeTaxInvalidPaymentDateError,
    IncomeTaxInvalidPeriodError,
    IncomeTaxInvalidTenantDocumentError,
)
from src.controller.income_tax_controller import (
    IncomeTaxController,
    InvalidIncomeTaxPeriodError,
)


def _item(category: str, amount: str, description: str = "Item") -> SimpleNamespace:
    return SimpleNamespace(
        key=f"{category}-{description}",
        category=SimpleNamespace(enumerator=category),
        amount=Decimal(amount),
        description=description,
    )


def _extract(
    tenant_document_number: str = "529.982.247-25",
) -> SimpleNamespace:
    return SimpleNamespace(
        key="extract-key",
        month_ref=1,
        year_ref=2026,
        contract=SimpleNamespace(
            tenant=SimpleNamespace(
                name="Tenant",
                document_number=tenant_document_number,
            ),
            property=SimpleNamespace(property_name="Property"),
            room_name=None,
        ),
        items=[
            _item("rent", "1001.01", "Rent"),
            _item("interest", "10", "Interest"),
            _item("administration_fee", "100", "Fee"),
            _item("iptu", "50", "IPTU"),
            _item("water", "999", "Non-deductible"),
        ],
        batch=SimpleNamespace(
            payment=SimpleNamespace(payment_date="2026-01-10"),
        ),
    )


def _participation(
    percentage: str = "50",
    owner_key: str = "owner-key",
    owner_name: str = "Owner",
) -> SimpleNamespace:
    return SimpleNamespace(
        participation_percentage=Decimal(percentage),
        owner=SimpleNamespace(key=owner_key, name=owner_name),
    )


def _controller(repository: Mock) -> IncomeTaxController:
    owner_repository = Mock()
    owner_repository.get_by_key.return_value = SimpleNamespace(
        key="owner-key",
        name="Owner",
        id=1,
    )
    return IncomeTaxController(owner_repository, repository)


def test_build_summary_applies_owner_share_and_excludes_non_tax_items():
    repository = Mock()
    repository.get_paid_extracts_for_period.return_value = [
        (_extract(), _participation()),
    ]

    summary = _controller(repository).get_summary(
        owner_key="owner-key",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    assert summary.total_income == 505.51
    assert summary.total_deductions == 50
    assert summary.taxable_base == 455.51
    assert summary.extracts[0].tenant_document_type == "PF"
    assert summary.extracts[0].income_items[-1].category == "interest"
    assert all(item.category != "water" for item in summary.extracts[0].income_items)
    assert summary.extracts[0].iptu == 0
    assert all(
        item.category != "iptu"
        for item in summary.extracts[0].deduction_items
    )
    assert summary.start_date == "2026-01-01"
    assert summary.end_date == "2026-01-31"
    assert summary.extracts[0].owner_name == "Owner"
    repository.get_paid_extracts_for_period.assert_called_once_with(
        owner_id=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )


def test_export_csv_uses_headerless_brazilian_format():
    repository = Mock()
    repository.get_paid_extracts_for_period.return_value = [
        (_extract(), _participation()),
    ]
    controller = _controller(repository)
    content, _ = controller.export_csv(
        owner_key="owner-key",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )
    rows = content.splitlines()

    assert rows == [
        "10/01/2026;R01.003.001;;505,51;50,00;Aluguel ref. 01/2026 - Property - Tenant;PF"
    ]


def test_summary_filters_by_tenant_type_before_calculating_totals():
    repository = Mock()
    repository.get_paid_extracts_for_period.return_value = [
        (_extract(), _participation()),
        (
            _extract("04.252.011/0001-10"),
            _participation(owner_key="owner-pj", owner_name="Owner PJ"),
        ),
    ]

    summary = _controller(repository).get_summary(
        owner_key="owner-key",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        tenant_type=IncomeTaxTenantType.PJ,
    )

    assert len(summary.extracts) == 1
    assert summary.extracts[0].tenant_document_type == "PJ"
    assert summary.total_income == 505.51
    assert summary.total_deductions == 50


def test_controller_translates_invalid_tenant_document_to_api_error():
    repository = Mock()
    repository.get_paid_extracts_for_period.return_value = [
        (_extract("invalid"), _participation("100")),
    ]

    with pytest.raises(IncomeTaxInvalidTenantDocumentError):
        _controller(repository).get_summary(
            owner_key="owner-key",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )


def test_controller_translates_invalid_payment_date_to_api_error():
    repository = Mock()
    extract = _extract()
    extract.batch.payment.payment_date = "not-a-date"
    repository.get_paid_extracts_for_period.return_value = [
        (extract, _participation("100")),
    ]

    with pytest.raises(IncomeTaxInvalidPaymentDateError):
        _controller(repository).get_summary(
            owner_key="owner-key",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )


def test_resolve_period_defaults_to_exactly_90_days_including_today():
    today = date(2026, 10, 21)

    start_date, end_date = IncomeTaxController.resolve_period(
        start_date=None,
        end_date=None,
        today=today,
    )

    assert start_date == today - timedelta(days=89)
    assert end_date == today


def test_resolve_period_supports_one_sided_date_filters():
    today = date(2026, 10, 21)
    start_date = date(2026, 1, 1)
    end_date = date(2026, 3, 31)

    assert IncomeTaxController.resolve_period(start_date, None, today) == (
        start_date,
        today,
    )
    assert IncomeTaxController.resolve_period(None, end_date, today) == (
        None,
        end_date,
    )


def test_controller_converts_reversed_date_range_to_api_error():
    controller = IncomeTaxController(Mock(), Mock())

    with pytest.raises(IncomeTaxInvalidPeriodError):
        controller.get_summary(
            owner_key=None,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 1, 1),
        )


def test_controller_rejects_reversed_date_range():
    with pytest.raises(InvalidIncomeTaxPeriodError):
        IncomeTaxController.resolve_period(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 1, 31),
            today=date(2026, 2, 2),
        )
