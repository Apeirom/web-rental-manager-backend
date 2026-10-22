import csv
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from io import StringIO

from src.constants.income_tax_constants import (
    INCOME_TAX_CENT,
    INCOME_TAX_DEFAULT_PERIOD_DAYS,
    INCOME_TAX_DEDUCTION_CATEGORIES,
    INCOME_TAX_INCOME_CATEGORIES,
    INCOME_TAX_INCOME_CODE,
)
from src.constants.property_constants import EQUITY_PARTICIPATION_PERCENTAGE_BASE
from src.dto.income_tax_dto import (
    IncomeTaxExtractDTO,
    IncomeTaxItemDTO,
    IncomeTaxSummaryDTO,
)
from src.errors.custom_errors import (
    IncomeTaxInvalidPeriodError,
    IncomeTaxInvalidPaymentDateError,
    IncomeTaxInvalidTenantDocumentError,
    OwnerNotFoundError,
)
from src.models import ExtractItemModel, ExtractModel
from src.models.equity_participation_model import EquityParticipationModel
from src.models.owner_model import OwnerModel
from src.repository.income_tax_repository import IncomeTaxRepository
from src.repository.owner_repository import OwnerRepository
from src.utils.document_number import document_number_type


class InvalidIncomeTaxTenantDocumentError(ValueError):
    def __init__(self, tenant_name: str):
        self.tenant_name = tenant_name
        super().__init__(tenant_name)


class InvalidIncomeTaxPaymentDateError(ValueError):
    def __init__(self, payment_date: str):
        self.payment_date = payment_date
        super().__init__(payment_date)


class InvalidIncomeTaxPeriodError(ValueError):
    def __init__(self, start_date: date, end_date: date):
        self.start_date = start_date
        self.end_date = end_date
        super().__init__("start_date must be on or before end_date")


def _money(value: Decimal | float | int) -> Decimal:
    return Decimal(str(value)).quantize(INCOME_TAX_CENT, rounding=ROUND_HALF_UP)


def _item_amount(item: ExtractItemModel) -> Decimal:
    return _money(abs(item.amount))


def _payment_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        try:
            return datetime.fromisoformat(value).date()
        except ValueError as error:
            raise InvalidIncomeTaxPaymentDateError(value) from error


def _brl(value: Decimal) -> str:
    return f"{value:.2f}".replace(".", ",")


class IncomeTaxController:
    def __init__(
        self,
        owner_repository: OwnerRepository,
        income_tax_repository: IncomeTaxRepository,
    ):
        self.owner_repository = owner_repository
        self.income_tax_repository = income_tax_repository

    @staticmethod
    def resolve_period(
        start_date: date | None,
        end_date: date | None,
        today: date | None = None,
    ) -> tuple[date | None, date]:
        current_date = today or date.today()
        if start_date is None and end_date is None:
            return (
                current_date - timedelta(days=INCOME_TAX_DEFAULT_PERIOD_DAYS - 1),
                current_date,
            )

        effective_end_date = end_date or current_date
        if start_date is not None and start_date > effective_end_date:
            raise InvalidIncomeTaxPeriodError(start_date, effective_end_date)
        return start_date, effective_end_date

    def get_summary(
        self,
        owner_key: str | None,
        start_date: date | None,
        end_date: date | None,
    ) -> IncomeTaxSummaryDTO:
        owner: OwnerModel | None = None
        if owner_key is not None:
            owner = self.owner_repository.get_by_key(owner_key)
            if owner is None:
                raise OwnerNotFoundError(owner_key=owner_key)

        try:
            return self._build_summary(
                owner_key=owner.key if owner else None,
                owner_name=owner.name if owner else None,
                owner_id=owner.id if owner else None,
                start_date=start_date,
                end_date=end_date,
            )
        except InvalidIncomeTaxPeriodError as error:
            raise IncomeTaxInvalidPeriodError(
                start_date=error.start_date.isoformat(),
                end_date=error.end_date.isoformat(),
            ) from error
        except InvalidIncomeTaxTenantDocumentError as error:
            raise IncomeTaxInvalidTenantDocumentError(
                tenant_name=error.tenant_name,
            ) from error
        except InvalidIncomeTaxPaymentDateError as error:
            raise IncomeTaxInvalidPaymentDateError(
                payment_date=error.payment_date,
            ) from error

    def _build_summary(
        self,
        owner_key: str | None,
        owner_name: str | None,
        owner_id: int | None,
        start_date: date | None,
        end_date: date | None,
    ) -> IncomeTaxSummaryDTO:
        effective_start_date, effective_end_date = self.resolve_period(
            start_date,
            end_date,
        )
        extracts = self.income_tax_repository.get_paid_extracts_for_period(
            owner_id=owner_id,
            start_date=effective_start_date,
            end_date=effective_end_date,
        )
        extract_dtos: list[IncomeTaxExtractDTO] = []
        for extract, participation in extracts:
            extract_dtos.append(self._build_extract_dto(extract, participation))

        total_income = _money(
            sum(
                (Decimal(str(row.total_income)) for row in extract_dtos),
                Decimal("0"),
            )
        )
        total_deductions = _money(
            sum(
                (Decimal(str(row.total_deductions)) for row in extract_dtos),
                Decimal("0"),
            )
        )

        return IncomeTaxSummaryDTO(
            owner_key=owner_key,
            owner_name=owner_name,
            start_date=(
                effective_start_date.isoformat()
                if effective_start_date is not None
                else None
            ),
            end_date=effective_end_date.isoformat(),
            total_income=float(total_income),
            total_deductions=float(total_deductions),
            taxable_base=float(_money(total_income - total_deductions)),
            extracts=extract_dtos,
        )

    def _build_extract_dto(
        self,
        extract: ExtractModel,
        participation: EquityParticipationModel,
    ) -> IncomeTaxExtractDTO:
        contract = extract.contract
        tenant = contract.tenant
        try:
            tenant_document_type = document_number_type(tenant.document_number)
        except ValueError as error:
            raise InvalidIncomeTaxTenantDocumentError(tenant.name) from error

        property_name = contract.property.property_name
        if contract.room_name:
            property_name = f"{property_name} - {contract.room_name}"

        share = (
            Decimal(str(participation.participation_percentage))
            / EQUITY_PARTICIPATION_PERCENTAGE_BASE
        )
        income_totals = {
            category: Decimal("0")
            for category in INCOME_TAX_INCOME_CATEGORIES
        }
        deduction_totals = {
            category: Decimal("0")
            for category in INCOME_TAX_DEDUCTION_CATEGORIES
        }

        for item in extract.items:
            category = item.category.enumerator
            amount = _item_amount(item)
            if category in income_totals:
                income_totals[category] += amount
            elif category in deduction_totals:
                deduction_totals[category] += amount

        income_totals = {
            category: _money(amount * share)
            for category, amount in income_totals.items()
        }
        deduction_totals = {
            category: _money(amount * share)
            for category, amount in deduction_totals.items()
        }
        total_income = _money(sum(income_totals.values(), Decimal("0")))
        total_deductions = _money(sum(deduction_totals.values(), Decimal("0")))
        payment = extract.batch.payment
        received_date = _payment_date(payment.payment_date)

        income_items = [
            IncomeTaxItemDTO(
                key=item.key,
                category=item.category.enumerator,
                description=item.description,
                amount=float(_money(_item_amount(item) * share)),
            )
            for item in extract.items
            if item.category.enumerator in INCOME_TAX_INCOME_CATEGORIES
        ]
        deduction_items = [
            IncomeTaxItemDTO(
                key=item.key,
                category=item.category.enumerator,
                description=item.description,
                amount=float(_money(_item_amount(item) * share)),
            )
            for item in extract.items
            if item.category.enumerator in INCOME_TAX_DEDUCTION_CATEGORIES
        ]

        return IncomeTaxExtractDTO(
            extract_key=extract.key,
            owner_key=participation.owner.key,
            owner_name=participation.owner.name,
            reference_date=f"{extract.month_ref:02d}/{extract.year_ref}",
            payment_date=received_date.isoformat(),
            tenant_name=tenant.name,
            tenant_document_number=tenant.document_number,
            tenant_document_type=tenant_document_type,
            property_name=property_name,
            participation_percentage=float(participation.participation_percentage),
            rent=float(income_totals["rent"]),
            interest=float(income_totals["interest"]),
            penalty=float(income_totals["penalty"]),
            administration_fee=float(deduction_totals["administration_fee"]),
            iptu=0.0,
            total_income=float(total_income),
            total_deductions=float(total_deductions),
            taxable_base=float(_money(total_income - total_deductions)),
            income_items=income_items,
            deduction_items=deduction_items,
        )

    def export_csv(
        self,
        owner_key: str | None,
        start_date: date | None,
        end_date: date | None,
    ) -> tuple[str, IncomeTaxSummaryDTO]:
        summary = self.get_summary(owner_key, start_date, end_date)
        output = StringIO(newline="")
        writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
        for extract in summary.extracts:
            received_date = _payment_date(extract.payment_date)
            history = (
                f"Aluguel ref. {extract.reference_date} - "
                f"{extract.property_name} - {extract.tenant_name}"
            )
            if summary.owner_key is None:
                history = f"{history} - {extract.owner_name}"
            writer.writerow(
                [
                    received_date.strftime("%d/%m/%Y"),
                    INCOME_TAX_INCOME_CODE,
                    "",
                    _brl(_money(extract.total_income)),
                    (
                        _brl(_money(extract.total_deductions))
                        if extract.total_deductions
                        else ""
                    ),
                    history,
                    extract.tenant_document_type,
                ]
            )
        return output.getvalue(), summary
