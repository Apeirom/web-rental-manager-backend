import pytest
from unittest.mock import patch

@pytest.fixture
def base_contract_key(auth_client):
    tenant_res = auth_client.post("/tenants", json={"name": "Extract Tenant", "document_number": "555.555.555-55"})
    tenant_key = tenant_res.json()["key"]

    prop_res = auth_client.post("/properties", json={"property_name": "Extract Prop", "owner_name": "Owner", "address": "789 St", "room_count": 2})
    property_key = prop_res.json()["key"]

    contract_payload = {
        "guarantee_type": "deposit",
        "rental_deposit": 2000.00,
        "rent_amount": 1000.00,
        "property_key": property_key,
        "tenant_key": tenant_key
    }
    contract_res = auth_client.post("/contracts", json=contract_payload)
    return contract_res.json()["key"]

def test_create_extract_success(auth_client, base_contract_key):
    payload = {
        "month_ref": 1,
        "year_ref": 2027,
        "rent_amount": 1000.00,
        "iptu": 150.00,
        "water": 50.00,
        "agreement": 0.00,
        "contract_key": base_contract_key
    }
    response = auth_client.post("/extracts", json=payload)
    
    assert response.status_code == 201
    assert response.json()["iptu"] == 150.00
    assert response.json()["contract"]["key"] == base_contract_key
    assert "key" in response.json()

def test_create_extract_invalid_contract(auth_client):
    payload = {
        "month_ref": 2,
        "year_ref": 2027,
        "contract_key": "invalid-contract-key"
    }
    response = auth_client.post("/extracts", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0014"

def test_get_all_extracts(auth_client, base_contract_key):
    payload = {
        "month_ref": 6,
        "year_ref": 2027,
        "rent_amount": 1000.00,
        "contract_key": base_contract_key
    }
    auth_client.post("/extracts", json=payload)

    response = auth_client.get("/extracts")
    assert response.status_code == 200
    res_json = response.json()
    assert "total" in res_json
    assert "skip" in res_json
    assert "limit" in res_json
    assert isinstance(res_json["data"], list)
    assert len(res_json["data"]) >= 1

def test_get_all_extracts_with_params(auth_client, base_contract_key):
    response = auth_client.get("/extracts?skip=0&limit=5&only_active_contracts=true")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["skip"] == 0
    assert res_json["limit"] == 5
    assert isinstance(res_json["data"], list)

def test_get_extract_by_key(auth_client, base_contract_key):
    payload = {
        "month_ref": 3,
        "year_ref": 2027,
        "rent_amount": 1000.00,
        "contract_key": base_contract_key
    }
    create_res = auth_client.post("/extracts", json=payload)
    extract_key = create_res.json()["key"]

    response = auth_client.get(f"/extracts/{extract_key}")
    assert response.status_code == 200
    assert response.json()["month_ref"] == 3
    assert response.json()["contract"]["rent_amount"] == 1000.00

def test_update_extract(auth_client, base_contract_key):
    payload = {
        "month_ref": 4,
        "year_ref": 2027,
        "rent_amount": 1000.00,
        "contract_key": base_contract_key
    }
    create_res = auth_client.post("/extracts", json=payload)
    extract_key = create_res.json()["key"]

    update_payload = {
        "month_ref": 4,
        "year_ref": 2027,
        "rent_amount": 1100.00,
        "iptu": 50.00,
        "water": 0.00,
        "agreement": 0.00,
        "contract_key": base_contract_key
    }
    update_res = auth_client.put(f"/extracts/{extract_key}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["rent_amount"] == 1100.00
    assert update_res.json()["iptu"] == 50.00

def test_delete_extract(auth_client, base_contract_key):
    payload = {
        "month_ref": 5,
        "year_ref": 2027,
        "contract_key": base_contract_key
    }
    create_res = auth_client.post("/extracts", json=payload)
    extract_key = create_res.json()["key"]

    delete_res = auth_client.delete(f"/extracts/{extract_key}")
    assert delete_res.status_code == 204

def test_upload_extract_receipt(auth_client, base_contract_key):
    payload = {
        "month_ref": 10,
        "year_ref": 2026,
        "rent_amount": 1000.00,
        "iptu": 150.00,
        "water": 50.00,
        "contract_key": base_contract_key
    }
    create_res = auth_client.post("/extracts", json=payload)
    extract_key = create_res.json()["key"]

    with patch("src.connectors.S3_storage_connector.S3StorageConnector.upload_file") as mock_upload:
        mock_upload.return_value = f"https://fake-supabase.com/extracts/{extract_key}_v1.pdf"

        file_data = {"file": ("comprovante.pdf", b"Conteudo em bytes do comprovante", "application/pdf")}
        response = auth_client.post(f"/extracts/{extract_key}/upload-receipt", files=file_data)

        assert response.status_code == 200
        assert response.json()["file_path"] == f"https://fake-supabase.com/extracts/{extract_key}_v1.pdf"
        mock_upload.assert_called_once()

def test_reconcile_extract_pending_no_autolink(auth_client, base_contract_key):
    extract_payload = {
        "month_ref": 11,
        "year_ref": 2026,
        "rent_amount": 1900.00,
        "contract_key": base_contract_key
    }
    extract_res = auth_client.post("/extracts", json=extract_payload)
    extract_key = extract_res.json()["key"]
    
    payment_res = auth_client.post("/payments", json={
        "payment_date": "2026-11-10",
        "amount": 1900.00
    })
    payment_key = payment_res.json()["key"]

    recon_res = auth_client.get(f"/extracts/{extract_key}/reconcile")
    
    assert recon_res.status_code == 200
    recon_data = recon_res.json()
    
    assert recon_data["status"] == "pending"
    assert recon_data["candidates"] is not None
    assert len(recon_data["candidates"]) == 1
    assert recon_data["candidates"][0]["key"] == payment_key
    assert recon_data["candidates"][0]["status"] == "unlinked"