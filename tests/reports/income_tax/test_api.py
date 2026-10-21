import csv
from io import StringIO


def _create_report_contracts(
    owner_factory,
    property_factory,
    tenant_factory,
    contract_factory,
):
    owner_x = owner_factory(name="Owner X")
    owner_y = owner_factory(name="Owner Y")
    tenant_one = tenant_factory(name="Tenant One")
    tenant_two = tenant_factory(
        name="Tenant Two",
        document_number="04.252.011/0001-10",
    )

    property_one = property_factory(
        property_name="Property One",
        equity_participations=[
            {
                "owner_key": owner_x["key"],
                "participation_percentage": 100,
            }
        ],
    )
    property_two = property_factory(
        property_name="Property Two",
        equity_participations=[
            {
                "owner_key": owner_x["key"],
                "participation_percentage": 50,
            },
            {
                "owner_key": owner_y["key"],
                "participation_percentage": 25,
            },
        ],
    )
    contract_one = contract_factory(
        payload={
            "property_key": property_one["key"],
            "tenant_key": tenant_one["key"],
            "rent_amount": 1000,
        }
    )
    contract_two = contract_factory(
        payload={
            "property_key": property_two["key"],
            "tenant_key": tenant_two["key"],
            "rent_amount": 2000,
        }
    )
    return owner_x, owner_y, contract_one, contract_two


def _paid_batch(
    extract_batch_factory,
    payment_factory,
    contract_key,
    items,
    payment_date,
    month_ref=1,
):
    batch = extract_batch_factory(
        contract_key=contract_key,
        month_ref=month_ref,
        year_ref=2026,
        items=items,
    )
    payment_factory(
        payment_date=payment_date,
        amount=1000,
        extract_batch_key=batch["key"],
        link=True,
    )
    return batch


def _tax_items(rent, interest, penalty, administration_fee, iptu):
    return [
        {
            "category": "rent",
            "description": "Aluguel",
            "amount": rent,
            "is_credit": True,
            "is_withheld_at_source": False,
        },
        {
            "category": "interest",
            "description": "Juros",
            "amount": interest,
            "is_credit": True,
            "is_withheld_at_source": False,
        },
        {
            "category": "penalty",
            "description": "Multa",
            "amount": penalty,
            "is_credit": True,
            "is_withheld_at_source": False,
        },
        {
            "category": "administration_fee",
            "description": "Taxa de administração",
            "amount": administration_fee,
            "is_credit": False,
            "is_withheld_at_source": True,
        },
        {
            "category": "iptu",
            "description": "IPTU",
            "amount": iptu,
            "is_credit": False,
            "is_withheld_at_source": True,
        },
        {
            "category": "water",
            "description": "Conta de água não dedutível",
            "amount": 999,
            "is_credit": False,
            "is_withheld_at_source": True,
        },
    ]


def test_income_tax_summary_applies_each_property_share_and_requires_payment(
    auth_client,
    owner_factory,
    property_factory,
    tenant_factory,
    contract_factory,
    extract_batch_factory,
    payment_factory,
):
    owner_x, owner_y, contract_one, contract_two = _create_report_contracts(
        owner_factory,
        property_factory,
        tenant_factory,
        contract_factory,
    )
    _paid_batch(
        extract_batch_factory,
        payment_factory,
        contract_one["key"],
        _tax_items(1000, 50, 25, 100, 50),
        "2026-01-10",
    )
    _paid_batch(
        extract_batch_factory,
        payment_factory,
        contract_two["key"],
        _tax_items(2000, 100, 50, 200, 100),
        "2026-01-20",
    )
    extract_batch_factory(
        contract_key=contract_one["key"],
        month_ref=1,
        year_ref=2026,
        items=_tax_items(9000, 0, 0, 0, 0),
    )

    response = auth_client.get(
        "/reports/income-tax/summary",
        params={
            "owner_key": owner_x["key"],
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        },
    )

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_income"] == 2150
    assert summary["total_deductions"] == 300
    assert summary["taxable_base"] == 1850
    assert summary["owner_name"] == "Owner X"
    assert summary["start_date"] == "2026-01-01"
    assert summary["end_date"] == "2026-01-31"
    assert len(summary["extracts"]) == 2
    by_property = {row["property_name"]: row for row in summary["extracts"]}
    assert by_property["Property One"]["participation_percentage"] == 100
    assert by_property["Property One"]["total_income"] == 1075
    assert by_property["Property Two"]["participation_percentage"] == 50
    assert by_property["Property Two"]["total_income"] == 1075
    assert by_property["Property One"]["total_deductions"] == 150
    assert by_property["Property Two"]["total_deductions"] == 150
    assert by_property["Property One"]["tenant_document_type"] == "PF"
    assert by_property["Property Two"]["tenant_document_type"] == "PJ"
    assert by_property["Property One"]["payment_date"] == "2026-01-10"

    other_owner_response = auth_client.get(
        "/reports/income-tax/summary",
        params={
            "owner_key": owner_y["key"],
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        },
    )
    assert other_owner_response.status_code == 200
    other_summary = other_owner_response.json()
    assert len(other_summary["extracts"]) == 1
    assert other_summary["extracts"][0]["participation_percentage"] == 25
    assert other_summary["total_income"] == 537.5
    assert other_summary["total_deductions"] == 75


def test_income_tax_export_has_seven_headerless_fields_and_brazilian_numbers(
    auth_client,
    owner_factory,
    property_factory,
    tenant_factory,
    contract_factory,
    extract_batch_factory,
    payment_factory,
):
    owner = owner_factory(name="CSV Owner")
    tenant = tenant_factory(
        name="Tenant PJ",
        document_number="04.252.011/0001-10",
    )
    property_record = property_factory(
        property_name="CSV Property",
        equity_participations=[
            {"owner_key": owner["key"], "participation_percentage": 50}
        ],
    )
    contract = contract_factory(
        payload={
            "property_key": property_record["key"],
            "tenant_key": tenant["key"],
            "rent_amount": 2000,
        }
    )
    _paid_batch(
        extract_batch_factory,
        payment_factory,
        contract["key"],
        _tax_items(1234.5, 0, 0, 0, 0),
        "2026-01-09",
    )
    _paid_batch(
        extract_batch_factory,
        payment_factory,
        contract["key"],
        _tax_items(500, 0, 0, 100, 0),
        "2026-01-15",
    )

    response = auth_client.get(
        "/reports/income-tax/export",
        params={
            "owner_key": owner["key"],
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment;" in response.headers["content-disposition"]
    rows = list(csv.reader(StringIO(response.text), delimiter=";"))
    assert len(rows) == 2
    assert all(len(row) == 7 for row in rows)
    assert rows[0] == [
        "09/01/2026",
        "R01.003.001",
        "",
        "617,25",
        "",
        "Aluguel ref. 01/2026 - CSV Property - Tenant PJ",
        "PJ",
    ]
    assert rows[1][1] == "R01.003.001"
    assert rows[1][2] == ""
    assert rows[1][3] == "250,00"
    assert rows[1][4] == "50,00"
    assert rows[1][6] == "PJ"


def test_income_tax_routes_require_owner_and_valid_period(auth_client):
    all_owners = auth_client.get(
        "/reports/income-tax/summary",
    )
    invalid_period = auth_client.get(
        "/reports/income-tax/summary",
        params={
            "start_date": "2026-02-01",
            "end_date": "2026-01-31",
        },
    )
    unknown_owner = auth_client.get(
        "/reports/income-tax/summary",
        params={
            "owner_key": "unknown-owner",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        },
    )

    assert all_owners.status_code == 200
    assert invalid_period.status_code == 422
    assert unknown_owner.status_code == 404


def test_income_tax_summary_applies_payment_date_bounds_inclusively(
    auth_client,
    owner_factory,
    property_factory,
    tenant_factory,
    contract_factory,
    extract_batch_factory,
    payment_factory,
):
    owner = owner_factory(name="Date Range Owner")
    property_record = property_factory(
        equity_participations=[
            {"owner_key": owner["key"], "participation_percentage": 100}
        ]
    )
    tenant = tenant_factory(name="Date Range Tenant")
    contract = contract_factory(
        payload={
            "property_key": property_record["key"],
            "tenant_key": tenant["key"],
        }
    )
    for payment_date in [
        "2025-12-31",
        "2026-01-10",
        "2026-01-20",
        "2026-01-31",
        "2026-02-01",
    ]:
        batch = extract_batch_factory(
            contract_key=contract["key"],
            month_ref=12,
            year_ref=2025,
        )
        payment_factory(
            payment_date=payment_date,
            extract_batch_key=batch["key"],
            link=True,
        )

    response = auth_client.get(
        "/reports/income-tax/summary",
        params={
            "owner_key": owner["key"],
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        },
    )

    assert response.status_code == 200
    summary = response.json()
    assert len(summary["extracts"]) == 3
    assert {row["payment_date"] for row in summary["extracts"]} == {
        "2026-01-10",
        "2026-01-20",
        "2026-01-31",
    }
    assert {row["reference_date"] for row in summary["extracts"]} == {"12/2025"}


def test_income_tax_summary_without_owner_returns_lines_per_owner(
    auth_client,
    owner_factory,
    property_factory,
    tenant_factory,
    contract_factory,
    extract_batch_factory,
    payment_factory,
):
    owner_one = owner_factory(name="First Owner")
    owner_two = owner_factory(name="Second Owner")
    property_record = property_factory(
        equity_participations=[
            {"owner_key": owner_one["key"], "participation_percentage": 60},
            {"owner_key": owner_two["key"], "participation_percentage": 40},
        ]
    )
    tenant = tenant_factory(name="Shared Property Tenant")
    contract = contract_factory(
        payload={
            "property_key": property_record["key"],
            "tenant_key": tenant["key"],
        }
    )
    batch = extract_batch_factory(
        contract_key=contract["key"],
        items=[
            {
                "category": "rent",
                "description": "Aluguel",
                "amount": 1000,
                "is_credit": True,
                "is_withheld_at_source": False,
            }
        ],
    )
    payment_factory(
        payment_date="2026-01-10",
        extract_batch_key=batch["key"],
        link=True,
    )

    response = auth_client.get(
        "/reports/income-tax/summary",
        params={"start_date": "2026-01-01", "end_date": "2026-01-31"},
    )

    assert response.status_code == 200
    summary = response.json()
    assert summary["owner_key"] is None
    assert len(summary["extracts"]) == 2
    assert {
        row["owner_name"]: row["total_income"]
        for row in summary["extracts"]
    } == {"First Owner": 600, "Second Owner": 400}
    assert summary["total_income"] == 1000

    export = auth_client.get(
        "/reports/income-tax/export",
        params={"start_date": "2026-01-01", "end_date": "2026-01-31"},
    )
    csv_rows = list(csv.reader(StringIO(export.text), delimiter=";"))
    assert len(csv_rows) == 2
    assert "First Owner" in csv_rows[0][5]
    assert "Second Owner" in csv_rows[1][5]


def test_old_income_tax_and_analysis_routes_are_removed(auth_client):
    old_income_tax = auth_client.get(
        "/income-tax/summary",
        params={
            "owner_key": "unknown-owner",
            "reference_month": 1,
            "reference_year": 2026,
        },
    )
    old_analysis = auth_client.get(
        "/analyses/income-tax",
        params={
            "start_year": 2026,
            "start_month": 1,
            "end_year": 2026,
            "end_month": 12,
        },
    )

    assert old_income_tax.status_code == 404
    assert old_analysis.status_code == 404
