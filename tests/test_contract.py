from unittest.mock import patch

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
        name="Swap Tenant", document_number="555.555.555-55"
    )["key"]
    property_key = property_factory(
        property_name="Studio Y", address="123"
    )["key"]

    g1_key = guarantee_factory(
        type="guarantor",
        name="Old Guarantor",
        document_number="333.333.333-33",
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
            "document_number": "888.777.666-55",
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

def test_upload_contract_document(auth_client, contract_factory):
    contract_key = contract_factory(
        payload={"rent_amount": 500.00},
        tenant_payload={
            "name": "Upload Tenant",
            "document_number": "111.111.111-11",
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

        file_data = {"file": ("contrato_falso.pdf", b"Conteudo em bytes do PDF", "application/pdf")}
        response = auth_client.post(f"/contracts/{contract_key}/upload-document", files=file_data)

        assert response.status_code == 200
        assert response.json()["file_path"] == f"https://fake-supabase.com/contracts/{contract_key}_v1.pdf"
        mock_upload.assert_called_once()