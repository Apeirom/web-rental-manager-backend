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

def test_create_extract_batch_success(auth_client, base_contract_key):
    payload = {
        "extracts": [
            {
                "month_ref": 1,
                "year_ref": 2027,
                "rent_amount": 1000.00,
                "iptu": 150.00,
                "water": 50.00,
                "agreement": 0.00,
                "contract_key": base_contract_key
            }
        ]
    }
    response = auth_client.post("/extract-batches", json=payload)
    
    assert response.status_code == 201
    res_json = response.json()
    assert "key" in res_json
    assert len(res_json["extracts"]) == 1
    assert res_json["extracts"][0]["iptu"] == 150.00
    assert res_json["extracts"][0]["contract"]["key"] == base_contract_key
    assert "total_net_transfer" in res_json

def test_create_extract_batch_invalid_contract(auth_client):
    payload = {
        "extracts": [
            {
                "month_ref": 2,
                "year_ref": 2027,
                "contract_key": "invalid-contract-key"
            }
        ]
    }
    response = auth_client.post("/extract-batches", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "RM-0014"

def test_get_all_extract_batches(auth_client, base_contract_key):
    payload = {
        "extracts": [
            {
                "month_ref": 6,
                "year_ref": 2027,
                "rent_amount": 1000.00,
                "contract_key": base_contract_key
            }
        ]
    }
    auth_client.post("/extract-batches", json=payload)

    response = auth_client.get("/extract-batches")
    assert response.status_code == 200
    res_json = response.json()
    assert "total" in res_json
    assert isinstance(res_json["data"], list)

def test_get_all_extract_batches_with_params(auth_client, base_contract_key):
    response = auth_client.get("/extract-batches?skip=0&limit=5&only_active_contracts=true")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["skip"] == 0
    assert res_json["limit"] == 5

def test_get_individual_extract_from_batch(auth_client, base_contract_key):
    payload = {
        "extracts": [
            {
                "month_ref": 3,
                "year_ref": 2027,
                "rent_amount": 1000.00,
                "contract_key": base_contract_key
            }
        ]
    }
    create_res = auth_client.post("/extract-batches", json=payload)
    batch_key = create_res.json()["key"]
    extract_key = create_res.json()["extracts"][0]["key"]

    response = auth_client.get(f"/extract-batches/{batch_key}/extracts/{extract_key}")
    assert response.status_code == 200
    assert response.json()["month_ref"] == 3

def test_update_extract_batch(auth_client, base_contract_key):
    payload = {
        "extracts": [
            {
                "month_ref": 4,
                "year_ref": 2027,
                "rent_amount": 1000.00,
                "contract_key": base_contract_key
            }
        ]
    }
    create_res = auth_client.post("/extract-batches", json=payload)
    batch_key = create_res.json()["key"]
    extract_key = create_res.json()["extracts"][0]["key"]

    update_payload = {
        "extracts": [
            {
                "key": extract_key,
                "month_ref": 4,
                "year_ref": 2027,
                "rent_amount": 1100.00,
                "iptu": 50.00,
                "water": 0.00,
                "agreement": 0.00,
                "contract_key": base_contract_key
            }
        ]
    }
    update_res = auth_client.put(f"/extract-batches/{batch_key}", json=update_payload)
    assert update_res.status_code == 200
    assert update_res.json()["extracts"][0]["rent_amount"] == 1100.00

def test_delete_extract_batch_preserves_payment(auth_client, base_contract_key):
    ext_res = auth_client.post("/extract-batches", json={
        "extracts": [{"month_ref": 5, "year_ref": 2027, "rent_amount": 1000.00, "contract_key": base_contract_key}]
    })
    batch_key = ext_res.json()["key"]

    pay_res = auth_client.post("/payments", json={"payment_date": "2027-05-10", "amount": 1000.00})
    payment_key = pay_res.json()["key"]

    auth_client.put(f"/payments/{payment_key}", json={
        "payment_date": "2027-05-10", 
        "amount": 1000.00, 
        "extract_batch_key": batch_key
    })

    delete_res = auth_client.delete(f"/extract-batches/{batch_key}")
    assert delete_res.status_code == 204

    check_pay = auth_client.get(f"/payments/{payment_key}")
    assert check_pay.status_code == 200
    assert check_pay.json()["status"] == "unlinked"
    assert check_pay.json().get("extract_batch_key") is None

def test_upload_extract_batch_receipt(auth_client, base_contract_key):
    payload = {
        "extracts": [
            {
                "month_ref": 10,
                "year_ref": 2026,
                "rent_amount": 1000.00,
                "contract_key": base_contract_key
            }
        ]
    }
    create_res = auth_client.post("/extract-batches", json=payload)
    batch_key = create_res.json()["key"]

    with patch("src.connectors.S3_storage_connector.S3StorageConnector.upload_file") as mock_upload:
        mock_upload.return_value = f"https://fake-supabase.com/extracts/{batch_key}_v1.pdf"

        file_data = {"file": ("comprovante.pdf", b"Conteudo em bytes", "application/pdf")}
        response = auth_client.post(f"/extract-batches/{batch_key}/upload-receipt", files=file_data)

        assert response.status_code == 200
        assert response.json()["file_path"] == f"https://fake-supabase.com/extracts/{batch_key}_v1.pdf"

def test_reconcile_extract_batch_pending_no_autolink(auth_client, base_contract_key):
    extract_res = auth_client.post("/extract-batches", json={
        "extracts": [{"month_ref": 11, "year_ref": 2026, "rent_amount": 1900.00, "contract_key": base_contract_key}]
    })
    batch_key = extract_res.json()["key"]
    
    payment_res = auth_client.post("/payments", json={"payment_date": "2026-11-10", "amount": 1900.00})
    payment_key = payment_res.json()["key"]

    recon_res = auth_client.get(f"/extract-batches/{batch_key}/reconcile")
    assert recon_res.status_code == 200
    recon_data = recon_res.json()
    
    assert recon_data["status"] == "success"
    assert len(recon_data["candidates"]) == 1
    assert recon_data["candidates"][0]["key"] == payment_key

def test_reconcile_extract_batch_already_linked(auth_client, base_contract_key):
    extract_res = auth_client.post("/extract-batches", json={
        "extracts": [{"month_ref": 12, "year_ref": 2026, "rent_amount": 1900.00, "contract_key": base_contract_key}]
    })
    batch_key = extract_res.json()["key"]
    
    payment_res = auth_client.post("/payments", json={"payment_date": "2026-12-10", "amount": 1900.00})
    payment_key = payment_res.json()["key"]

    auth_client.put(f"/payments/{payment_key}", json={
        "payment_date": "2026-12-10", 
        "amount": 1900.00, 
        "extract_batch_key": batch_key
    })

    recon_res = auth_client.get(f"/extract-batches/{batch_key}/reconcile")
    assert recon_res.status_code == 200
    recon_data = recon_res.json()
    
    assert recon_data["status"] == "alreadyLinked"
    assert len(recon_data["candidates"]) == 1
    assert recon_data["candidates"][0]["key"] == payment_key

def test_update_extract_batch_delete_and_add_calculates_total_correctly(auth_client, base_contract_key):
    create_payload = {
        "extracts": [
            {
                "month_ref": 1,
                "year_ref": 2026,
                "rent_amount": 2000.00,
                "contract_key": base_contract_key
            }
        ]
    }
    create_res = auth_client.post("/extract-batches", json=create_payload)
    assert create_res.status_code == 201
    
    create_data = create_res.json()
    batch_key = create_data["key"]
    first_extract_key = create_data["extracts"][0]["key"]
    
    update_payload = {
        "extracts": [
            {
                "month_ref": 2,
                "year_ref": 2026,
                "rent_amount": 3000.00,
                "contract_key": base_contract_key
            }
        ]
    }
    update_res = auth_client.put(f"/extract-batches/{batch_key}", json=update_payload)
    assert update_res.status_code == 200
    
    update_data = update_res.json()
    
    assert len(update_data["extracts"]) == 1
    new_extract_key = update_data["extracts"][0]["key"]
    assert new_extract_key != first_extract_key
    
    expected_net_transfer = update_data["extracts"][0]["net_transfer"]
    assert update_data["total_net_transfer"] == expected_net_transfer


def test_update_extract_batch_complex_scenario_calculates_total_correctly(auth_client, base_contract_key):
    create_payload = {
        "extracts": [
            {
                "month_ref": 1,
                "year_ref": 2026,
                "rent_amount": 1000.00,
                "contract_key": base_contract_key
            },
            {
                "month_ref": 1,
                "year_ref": 2026,
                "rent_amount": 2000.00,
                "contract_key": base_contract_key
            }
        ]
    }
    create_res = auth_client.post("/extract-batches", json=create_payload)
    assert create_res.status_code == 201
    
    create_data = create_res.json()
    batch_key = create_data["key"]
    extract_to_keep_key = create_data["extracts"][0]["key"]

    update_payload = {
        "extracts": [
            {
                "key": extract_to_keep_key,
                "month_ref": 1,
                "year_ref": 2026,
                "rent_amount": 1500.00,
                "contract_key": base_contract_key
            },
            {
                "month_ref": 2,
                "year_ref": 2026,
                "rent_amount": 3000.00,
                "contract_key": base_contract_key
            }
        ]
    }
    update_res = auth_client.put(f"/extract-batches/{batch_key}", json=update_payload)
    assert update_res.status_code == 200
    
    update_data = update_res.json()
    assert len(update_data["extracts"]) == 2

    total_calculated = 0.0
    for ext in update_data["extracts"]:
        total_calculated += ext["net_transfer"]

    assert update_data["total_net_transfer"] == total_calculated