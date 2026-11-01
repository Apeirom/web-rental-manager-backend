import pytest


def _create(client, path, payload):
    response = client.post(path, json=payload)
    assert response.status_code == 201, (
        f"Could not create test data at {path}: "
        f"{response.status_code} {response.text}"
    )
    return response.json()


@pytest.fixture
def owner_factory(auth_client):
    def create_owner(name="Fixture Owner", document_number=None, **overrides):
        payload = {"name": name}
        if document_number is not None:
            payload["document_number"] = document_number
        payload.update(overrides)
        return _create(auth_client, "/owners", payload)

    return create_owner


@pytest.fixture
def tenant_factory(auth_client):
    def create_tenant(
        name="Fixture Tenant",
        document_number=None,
        **overrides,
    ):
        if document_number is None:
            document_number = next(
                create_tenant.generated_documents,
                "100.000.000-19",
            )
        payload = {"name": name, "document_number": document_number}
        payload.update(overrides)
        return _create(auth_client, "/tenants", payload)

    create_tenant.generated_documents = iter(
        [
            "529.982.247-25",
            "111.444.777-35",
            "987.654.321-00",
            "100.000.000-19",
            "100.000.001-08",
        ]
    )
    return create_tenant


@pytest.fixture
def guarantee_factory(auth_client):
    def create_guarantee(payload=None, **overrides):
        if payload:
            guarantee_payload = dict(payload)
        elif overrides.get("type", "deposit") == "deposit":
            guarantee_payload = {"type": "deposit", "amount": 2000.00}
        else:
            guarantee_payload = {"type": overrides["type"]}
        guarantee_payload.update(overrides)
        return _create(auth_client, "/guarantees", guarantee_payload)

    return create_guarantee


@pytest.fixture
def real_estate_factory(auth_client):
    def create_real_estate(payload=None, **overrides):
        real_estate_payload = {
            "name": "Fixture Real Estate",
            "cnpj": "04.252.011/0001-10",
            "commission": 0.10,
            "address": "Fixture Address",
            "phone": "+5511999999999",
        }
        if payload is not None:
            real_estate_payload.update(payload)
        real_estate_payload.update(overrides)
        return _create(auth_client, "/real-estates", real_estate_payload)

    return create_real_estate


@pytest.fixture
def property_factory(auth_client, owner_factory):
    def create_property(
        property_name="Fixture Property",
        owner_key=None,
        owner_name="Fixture Owner",
        equity_participations=None,
        address="123 Fixture St",
        room_count=1,
        **overrides,
    ):
        if owner_key is None and equity_participations is None:
            owner_key = owner_factory(name=owner_name)["key"]

        payload = {
            "property_name": property_name,
            "address": address,
            "room_count": room_count,
        }
        if equity_participations is None:
            equity_participations = [
                {
                    "owner_key": owner_key,
                    "participation_percentage": 100,
                }
            ]
        payload["equity_participations"] = equity_participations
        payload.update(overrides)
        return _create(auth_client, "/properties", payload)

    return create_property


@pytest.fixture
def contract_factory(
    auth_client,
    tenant_factory,
    property_factory,
    guarantee_factory,
):
    def create_contract(
        payload=None,
        tenant_payload=None,
        property_payload=None,
        guarantee_payload=None,
        **overrides,
    ):
        contract_payload = {"rent_amount": 1000.00, "status": "active"}
        if payload is not None:
            contract_payload.update(payload)
        contract_payload.update(overrides)

        if not contract_payload.get("tenant_key"):
            contract_payload["tenant_key"] = tenant_factory(
                **(tenant_payload or {})
            )["key"]
        if not contract_payload.get("property_key"):
            contract_payload["property_key"] = property_factory(
                **(property_payload or {})
            )["key"]
        if not contract_payload.get("guarantee_key"):
            contract_payload["guarantee_key"] = guarantee_factory(
                guarantee_payload or {}
            )["key"]

        return _create(auth_client, "/contracts", contract_payload)

    return create_contract


@pytest.fixture
def extract_batch_factory(auth_client, contract_factory):
    def create_extract_batch(
        payload=None,
        contract_key=None,
        contract_payload=None,
        extracts=None,
        month_ref=1,
        year_ref=2026,
        items=None,
        **overrides,
    ):
        batch_payload = dict(payload or {})
        batch_payload.update(overrides)
        batch_extracts = batch_payload.get("extracts", extracts)

        if batch_extracts is None:
            batch_extracts = [
                {
                    "month_ref": month_ref,
                    "year_ref": year_ref,
                    "items": items
                    if items is not None
                    else [
                        {
                            "category": "rent",
                            "description": "Fixture Rent",
                            "amount": 1000.00,
                            "is_credit": True,
                            "is_withheld_at_source": False,
                        }
                    ],
                }
            ]

        if contract_key is None and not all(
            extract.get("contract_key") for extract in batch_extracts
        ):
            contract_key = contract_factory(
                payload=contract_payload
            )["key"]

        for extract in batch_extracts:
            extract.setdefault("contract_key", contract_key)

        batch_payload["extracts"] = batch_extracts
        batch_payload.setdefault("confirm_duplicate", overrides.get("confirm_duplicate", True))
        return _create(auth_client, "/extract-batches", batch_payload)

    return create_extract_batch


@pytest.fixture
def payment_factory(auth_client, extract_batch_factory):
    def create_payment(
        payment_date="2026-01-10",
        amount=1000.00,
        extract_batch_key=None,
        link=False,
        extract_batch_payload=None,
        **overrides,
    ):
        payload = {"payment_date": payment_date, "amount": amount}
        payload.update(overrides)
        payment = _create(auth_client, "/payments", payload)

        if link:
            if extract_batch_key is None:
                extract_batch_key = extract_batch_factory(
                    **(extract_batch_payload or {})
                )["key"]
            response = auth_client.put(
                f"/payments/{payment['key']}",
                json={
                    "payment_date": payment_date,
                    "amount": amount,
                    "extract_batch_key": extract_batch_key,
                },
            )
            assert response.status_code == 200, (
                "Could not link test payment to extract batch: "
                f"{response.status_code} {response.text}"
            )
            return response.json()

        return payment

    return create_payment


@pytest.fixture
def base_contract(contract_factory):
    return contract_factory()


@pytest.fixture
def base_contract_key(base_contract):
    return base_contract["key"]
