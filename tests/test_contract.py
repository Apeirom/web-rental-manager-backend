from unittest.mock import patch
import pytest


def test_create_contract_success(
    auth_client, tenant_factory, property_factory, guarantee_factory
):
    tenant_key = tenant_factory(name="John Tenant")["key"]

    property_key = property_factory(
        property_name="Apt 202",
        owner_name="Jane Owner",
        address="789 High St",
        room_count=3,
    )["key"]

    guarantee_key = guarantee_factory(amount=3000.00)["key"]

    payload = {
        "rent_amount": 1000.00,
        "room_name": "Suite A",
        "status": "active",
        "property_key": property_key,
        "tenant_key": tenant_key,
        "guarantee_key": guarantee_key
    }
    response = auth_client.post("/contracts", json=payload)
    
    assert response.status_code == 201
    assert response.json()["property"]["key"] == property_key
    assert response.json()["tenant"]["key"] == tenant_key
    assert response.json()["guarantee"]["type"] == "deposit"
    assert response.json()["guarantee"]["amount"] == 3000.00
    assert "key" in response.json()

def test_create_contract_invalid_guarantee(auth_client, tenant_factory, property_factory):
    tenant_key = tenant_factory(
        name="Jane Tenant", document_number="987.654.321-00"
    )["key"]

    property_key = property_factory(
        property_name="Apt 203",
        owner_name="Jane Owner",
        address="789 High St",
        room_count=3,
    )["key"]

    payload = {
        "rent_amount": 500.00,
        "property_key": property_key,
        "tenant_key": tenant_key,
        "guarantee_key": "non-existent-guarantee-key"
    }
    response = auth_client.post("/contracts", json=payload)
    assert response.status_code == 400

def test_update_contract_swap_guarantee_deletes_orphan(
    auth_client, tenant_factory, property_factory, guarantee_factory, contract_factory
):
    tenant_key = tenant_factory(
        name="Swap Tenant", document_number="111.444.777-35"
    )["key"]
    property_key = property_factory(
        property_name="Studio Y", address="123"
    )["key"]

    g1_key = guarantee_factory(
        type="guarantor",
        name="Old Guarantor",
        document_number="100.000.000-19",
    )["key"]
    contract_key = contract_factory(
        payload={
            "rent_amount": 1000.00,
            "property_key": property_key,
            "tenant_key": tenant_key,
            "guarantee_key": g1_key,
        }
    )["key"]

    g2_key = guarantee_factory(amount=2500.00)["key"]

    update_res = auth_client.put(f"/contracts/{contract_key}", json={
        "rent_amount": 1200.00,
        "property_key": property_key,
        "tenant_key": tenant_key,
        "guarantee_key": g2_key,
        "status": "active"
    })
    
    assert update_res.status_code == 200
    assert update_res.json()["guarantee"]["type"] == "deposit"
    
    check_g1 = auth_client.get(f"/guarantees/{g1_key}")
    assert check_g1.status_code == 404

def test_delete_contract(auth_client, contract_factory):
    contract_key = contract_factory(
        payload={"rent_amount": 500.00},
        tenant_payload={
            "name": "Tenant Two",
            "document_number": "100.000.001-08",
        },
        property_payload={
            "property_name": "Room 5",
            "owner_name": "Owner Two",
            "address": "789 Side St",
            "room_count": 1,
        },
        guarantee_payload={"type": "deposit", "amount": 500.00},
    )["key"]

    delete_res = auth_client.delete(f"/contracts/{contract_key}")
    assert delete_res.status_code == 204


def test_delete_contract_cleans_extracts_and_preserves_payment(
    auth_client,
    contract_factory,
    extract_batch_factory,
    payment_factory,
):
    contract = contract_factory(
        tenant_payload={"document_number": "529.982.247-25"}
    )
    surviving_contract = contract_factory(
        tenant_payload={"document_number": "111.444.777-35"}
    )
    batch = extract_batch_factory(
        extracts=[
            {
                "month_ref": 1,
                "year_ref": 2026,
                "contract_key": contract["key"],
                "items": [
                    {
                        "category": "rent",
                        "description": "First rent",
                        "amount": 1000.0,
                        "is_credit": True,
                        "is_withheld_at_source": False,
                    }
                ],
            },
            {
                "month_ref": 2,
                "year_ref": 2026,
                "contract_key": surviving_contract["key"],
                "items": [
                    {
                        "category": "rent",
                        "description": "Surviving rent",
                        "amount": 425.0,
                        "is_credit": True,
                        "is_withheld_at_source": False,
                    }
                ],
            },
        ]
    )
    payment = payment_factory(
        amount=1425.0,
        extract_batch_key=batch["key"],
        link=True,
    )

    response = auth_client.delete(f"/contracts/{contract['key']}")

    assert response.status_code == 204
    assert auth_client.get(f"/contracts/{contract['key']}").status_code == 404

    surviving_batch_res = auth_client.get(f"/extract-batches/{batch['key']}")
    assert surviving_batch_res.status_code == 200
    surviving_batch = surviving_batch_res.json()
    assert surviving_batch["total_net_transfer"] == 425.0
    assert len(surviving_batch["extracts"]) == 1

    payment_res = auth_client.get(f"/payments/{payment['key']}")
    assert payment_res.status_code == 200
    assert payment_res.json()["status"] == "unlinked"
    assert payment_res.json().get("extract_batch_key") is None

    remaining_extract_key = surviving_batch["extracts"][0]["key"]
    response = auth_client.delete(
        f"/extract-batches/{batch['key']}/extracts/{remaining_extract_key}"
    )
    assert response.status_code == 204
    assert auth_client.get(f"/extract-batches/{batch['key']}").status_code == 404

    final_payment_res = auth_client.get(f"/payments/{payment['key']}")
    assert final_payment_res.status_code == 200
    assert final_payment_res.json()["key"] == payment["key"]


@pytest.mark.parametrize(
    ("dependency", "route"),
    [
        ("property", "properties"),
        ("tenant", "tenants"),
        ("guarantee", "guarantees"),
    ],
)
def test_deleting_required_contract_dependency_deletes_contract(
    auth_client,
    contract_factory,
    dependency,
    route,
):
    contract = contract_factory()
    dependency_key = contract[dependency]["key"]

    response = auth_client.delete(f"/{route}/{dependency_key}")

    assert response.status_code == 204
    assert auth_client.get(f"/contracts/{contract['key']}").status_code == 404


def test_delete_real_estate_preserves_contract_and_clears_reference(
    auth_client,
    real_estate_factory,
    contract_factory,
):
    real_estate = real_estate_factory()
    contract = contract_factory(payload={"real_estate_key": real_estate["key"]})

    response = auth_client.delete(f"/real-estates/{real_estate['key']}")

    assert response.status_code == 204
    contract_res = auth_client.get(f"/contracts/{contract['key']}")
    assert contract_res.status_code == 200
    assert contract_res.json()["real_estate"] is None


def test_create_contract_requires_guarantee(
    auth_client,
    tenant_factory,
    property_factory,
):
    response = auth_client.post(
        "/contracts",
        json={
            "rent_amount": 1000,
            "status": "active",
            "tenant_key": tenant_factory()["key"],
            "property_key": property_factory()["key"],
        },
    )

    assert response.status_code == 422

def test_upload_contract_document(auth_client, contract_factory):
    contract_key = contract_factory(
        payload={"rent_amount": 500.00},
        tenant_payload={
            "name": "Upload Tenant",
            "document_number": "529.982.247-25",
        },
        property_payload={
            "property_name": "Upload Prop",
            "owner_name": "Owner",
            "address": "123",
            "room_count": 1,
        },
    )["key"]

    with patch("src.connectors.S3_storage_connector.S3StorageConnector.upload_file") as mock_upload:
        mock_upload.return_value = f"https://fake-supabase.com/contracts/{contract_key}_v1.pdf"

        file_data = {"file": ("contrato_falso.pdf", b"%PDF-1.4 Conteudo em bytes do PDF", "application/pdf")}
        response = auth_client.post(f"/contracts/{contract_key}/upload-document", files=file_data)

        assert response.status_code == 200
        assert response.json()["file_path"] == f"https://fake-supabase.com/contracts/{contract_key}_v1.pdf"
        mock_upload.assert_called_once()


def test_upload_contract_document_file_too_large(auth_client, base_contract_key):
    oversized_bytes = b"%PDF" + (b"0" * (10 * 1024 * 1024 + 1))
    file_data = {"file": ("contrato_grande.pdf", oversized_bytes, "application/pdf")}
    response = auth_client.post(f"/contracts/{base_contract_key}/upload-document", files=file_data)

    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "RM-0035"


def test_upload_contract_document_invalid_magic_bytes(auth_client, base_contract_key):
    file_data = {"file": ("malicioso.pdf", b"<script>alert(1)</script>", "application/pdf")}
    response = auth_client.post(f"/contracts/{base_contract_key}/upload-document", files=file_data)

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0036"
