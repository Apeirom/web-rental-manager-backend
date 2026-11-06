from unittest.mock import patch


def test_create_extract_batch_success(auth_client, base_contract_key):
    payload = {
        "extracts": [
            {
                "month_ref": 1,
                "year_ref": 2027,
                "contract_key": base_contract_key,
                "items": [
                    {"category": "rent", "description": "Aluguel", "amount": 1000.00, "is_credit": True, "is_withheld_at_source": False},
                    {"category": "iptu", "description": "IPTU", "amount": 150.00, "is_credit": False, "is_withheld_at_source": True},
                    {"category": "water", "description": "Água", "amount": 50.00, "is_credit": False, "is_withheld_at_source": True}
                ]
            }
        ]
    }
    response = auth_client.post("/extract-batches", json=payload)
    
    assert response.status_code == 201
    res_json = response.json()
    assert "key" in res_json
    assert len(res_json["extracts"]) == 1
    assert len(res_json["extracts"][0]["items"]) == 3
    assert res_json["extracts"][0]["contract"]["key"] == base_contract_key
    assert "total_net_transfer" in res_json

def test_create_extract_batch_invalid_contract(auth_client):
    payload = {
        "extracts": [
            {
                "month_ref": 2,
                "year_ref": 2027,
                "contract_key": "invalid-contract-key",
                "items": []
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
                "contract_key": base_contract_key,
                "items": [
                    {"category": "rent", "description": "Aluguel", "amount": 1000.00, "is_credit": True, "is_withheld_at_source": False}
                ]
            }
        ]
    }
    auth_client.post("/extract-batches", json=payload)

    response = auth_client.get("/extract-batches")
    assert response.status_code == 200
    res_json = response.json()
    assert "total" in res_json
    assert isinstance(res_json["data"], list)


def test_extract_batch_returns_all_property_owners_without_legacy_owner(
    auth_client,
    owner_factory,
    property_factory,
    contract_factory,
    extract_batch_factory,
):
    first_owner = owner_factory(name="First Owner")
    second_owner = owner_factory(name="Second Owner")
    property_record = property_factory(
        property_name="Shared property in extract",
        equity_participations=[
            {
                "owner_key": first_owner["key"],
                "participation_percentage": 50,
            },
            {
                "owner_key": second_owner["key"],
                "participation_percentage": 50,
            },
        ],
    )
    contract = contract_factory(
        payload={"property_key": property_record["key"]}
    )
    batch = extract_batch_factory(contract_key=contract["key"])

    response = auth_client.get("/extract-batches")

    assert response.status_code == 200
    batch_dto = next(
        item for item in response.json()["data"] if item["key"] == batch["key"]
    )
    property_dto = batch_dto["extracts"][0]["contract"]["property"]
    assert "owner" not in property_dto
    assert [
        participation["owner"]["name"]
        for participation in property_dto["equity_participations"]
    ] == ["First Owner", "Second Owner"]


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
                "contract_key": base_contract_key,
                "items": [
                    {"category": "rent", "description": "Aluguel", "amount": 1000.00, "is_credit": True, "is_withheld_at_source": False}
                ]
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
                "contract_key": base_contract_key,
                "items": [
                    {"category": "rent", "description": "Aluguel", "amount": 1000.00, "is_credit": True, "is_withheld_at_source": False}
                ]
            }
        ]
    }
    create_res = auth_client.post("/extract-batches", json=payload)
    batch_key = create_res.json()["key"]
    extract_key = create_res.json()["extracts"][0]["key"]
    item_key = create_res.json()["extracts"][0]["items"][0]["key"]

    update_payload = {
        "extracts": [
            {
                "key": extract_key,
                "month_ref": 4,
                "year_ref": 2027,
                "contract_key": base_contract_key,
                "items": [
                    {
                        "key": item_key,
                        "category": "rent", 
                        "description": "Aluguel Atualizado", 
                        "amount": 1100.00, 
                        "is_credit": True, 
                        "is_withheld_at_source": False
                    },
                    {
                        "category": "iptu", 
                        "description": "Novo IPTU", 
                        "amount": 50.00, 
                        "is_credit": False, 
                        "is_withheld_at_source": True
                    }
                ]
            }
        ]
    }
    update_res = auth_client.put(f"/extract-batches/{batch_key}", json=update_payload)
    assert update_res.status_code == 200
    updated_items = update_res.json()["extracts"][0]["items"]
    assert len(updated_items) == 2
    assert updated_items[0]["amount"] == 1100.00

def test_delete_extract_batch_preserves_payment(
    auth_client, base_contract_key, extract_batch_factory, payment_factory
):
    extract_batch = extract_batch_factory(
        contract_key=base_contract_key,
        month_ref=5,
        year_ref=2027,
        items=[
            {
                "category": "rent",
                "description": "Aluguel",
                "amount": 1000.0,
                "is_credit": True,
                "is_withheld_at_source": False,
            }
        ],
    )
    batch_key = extract_batch["key"]
    payment = payment_factory(
        payment_date="2027-05-10",
        amount=1000.00,
        extract_batch_key=batch_key,
        link=True,
    )
    payment_key = payment["key"]

    delete_res = auth_client.delete(f"/extract-batches/{batch_key}")
    assert delete_res.status_code == 204

    check_pay = auth_client.get(f"/payments/{payment_key}")
    assert check_pay.status_code == 200
    assert check_pay.json()["status"] == "unlinked"
    assert check_pay.json().get("extract_batch_key") is None


def test_delete_individual_extract_reconciles_batch_and_preserves_payment(
    auth_client,
    contract_factory,
    extract_batch_factory,
    payment_factory,
):
    first_contract = contract_factory(
        tenant_payload={"document_number": "529.982.247-25"}
    )
    second_contract = contract_factory(
        tenant_payload={"document_number": "111.444.777-35"}
    )
    batch = extract_batch_factory(
        extracts=[
            {
                "month_ref": 1,
                "year_ref": 2026,
                "contract_key": first_contract["key"],
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
                "contract_key": second_contract["key"],
                "items": [
                    {
                        "category": "rent",
                        "description": "Second rent",
                        "amount": 650.0,
                        "is_credit": True,
                        "is_withheld_at_source": False,
                    }
                ],
            },
        ]
    )
    payment = payment_factory(
        amount=1650.0,
        extract_batch_key=batch["key"],
        link=True,
    )
    extracts = batch["extracts"]
    first_extract = next(
        extract
        for extract in extracts
        if extract["contract"]["key"] == first_contract["key"]
    )
    second_extract = next(
        extract
        for extract in extracts
        if extract["contract"]["key"] == second_contract["key"]
    )

    first_extract_detail = auth_client.get(
        f"/extract-batches/{batch['key']}/extracts/{first_extract['key']}"
    )
    assert first_extract_detail.status_code == 200
    assert len(first_extract_detail.json()["items"]) > 0

    response = auth_client.delete(
        f"/extract-batches/{batch['key']}/extracts/{first_extract['key']}"
    )

    assert response.status_code == 204
    remaining_batch_res = auth_client.get(f"/extract-batches/{batch['key']}")
    assert remaining_batch_res.status_code == 200
    remaining_batch = remaining_batch_res.json()
    assert remaining_batch["total_net_transfer"] == 650.0
    assert len(remaining_batch["extracts"]) == 1

    assert auth_client.get(
        f"/extract-batches/{batch['key']}/extracts/{first_extract['key']}"
    ).status_code == 404

    payment_res = auth_client.get(f"/payments/{payment['key']}")
    assert payment_res.status_code == 200
    assert payment_res.json()["status"] == "unlinked"
    assert payment_res.json().get("extract_batch_key") is None

    response = auth_client.delete(
        f"/extract-batches/{batch['key']}/extracts/{second_extract['key']}"
    )

    assert response.status_code == 204
    assert auth_client.get(f"/extract-batches/{batch['key']}").status_code == 404
    after_second_payment = auth_client.get(f"/payments/{payment['key']}")
    assert after_second_payment.status_code == 200
    assert after_second_payment.json()["key"] == payment["key"]

def test_upload_extract_batch_receipt(auth_client, base_contract_key):
    payload = {
        "extracts": [
            {
                "month_ref": 10,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [{"category": "rent", "description": "Aluguel", "amount": 1000.00, "is_credit": True, "is_withheld_at_source": False}]
            }
        ]
    }
    create_res = auth_client.post("/extract-batches", json=payload)
    batch_key = create_res.json()["key"]

    with patch("src.connectors.S3_storage_connector.S3StorageConnector.upload_file") as mock_upload:
        mock_upload.return_value = f"https://fake-supabase.com/extracts/{batch_key}_v1.pdf"

        file_data = {"file": ("comprovante.pdf", b"%PDF-1.4 Conteudo em bytes", "application/pdf")}
        response = auth_client.post(f"/extract-batches/{batch_key}/upload-receipt", files=file_data)

        assert response.status_code == 200
        assert response.json()["file_path"] == f"https://fake-supabase.com/extracts/{batch_key}_v1.pdf"

def test_reconcile_extract_batch_pending_no_autolink(
    auth_client, base_contract_key, extract_batch_factory, payment_factory
):
    extract_batch = extract_batch_factory(
        contract_key=base_contract_key,
        month_ref=11,
        year_ref=2026,
        items=[
            {
                "category": "rent",
                "description": "Aluguel",
                "amount": 1900.00,
                "is_credit": True,
                "is_withheld_at_source": False,
            }
        ],
    )
    batch_key = extract_batch["key"]
    payment_key = payment_factory(
        payment_date="2026-11-10", amount=1900.00
    )["key"]

    recon_res = auth_client.get(f"/extract-batches/{batch_key}/reconcile")
    assert recon_res.status_code == 200
    recon_data = recon_res.json()
    
    assert recon_data["status"] == "success"
    assert len(recon_data["candidates"]) == 1
    assert recon_data["candidates"][0]["key"] == payment_key

def test_reconcile_extract_batch_already_linked(
    auth_client, base_contract_key, extract_batch_factory, payment_factory
):
    extract_batch = extract_batch_factory(
        contract_key=base_contract_key,
        month_ref=12,
        year_ref=2026,
        items=[
            {
                "category": "rent",
                "description": "Aluguel",
                "amount": 1900.00,
                "is_credit": True,
                "is_withheld_at_source": False,
            }
        ],
    )
    batch_key = extract_batch["key"]
    payment = payment_factory(
        payment_date="2026-12-10",
        amount=1900.00,
        extract_batch_key=batch_key,
        link=True,
    )
    payment_key = payment["key"]

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
                "contract_key": base_contract_key,
                "items": [{"category": "rent", "description": "Aluguel", "amount": 2000.0, "is_credit": True, "is_withheld_at_source": False}]
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
                "contract_key": base_contract_key,
                "items": [{"category": "rent", "description": "Aluguel", "amount": 3000.0, "is_credit": True, "is_withheld_at_source": False}]
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
        "confirm_duplicate": True,
        "extracts": [
            {
                "month_ref": 1,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [{"category": "rent", "description": "Aluguel 1", "amount": 1000.0, "is_credit": True, "is_withheld_at_source": False}]
            },
            {
                "month_ref": 1,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [{"category": "rent", "description": "Aluguel 2", "amount": 2000.0, "is_credit": True, "is_withheld_at_source": False}]
            }
        ]
    }
    create_res = auth_client.post("/extract-batches", json=create_payload)
    assert create_res.status_code == 201
    
    create_data = create_res.json()
    batch_key = create_data["key"]
    extract_to_keep_key = create_data["extracts"][0]["key"]
    item_to_keep_key = create_data["extracts"][0]["items"][0]["key"]

    update_payload = {
        "extracts": [
            {
                "key": extract_to_keep_key,
                "month_ref": 1,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [{"key": item_to_keep_key, "category": "rent", "description": "Aluguel 1 Modificado", "amount": 1500.0, "is_credit": True, "is_withheld_at_source": False}]
            },
            {
                "month_ref": 2,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [{"category": "rent", "description": "Aluguel Novo", "amount": 3000.0, "is_credit": True, "is_withheld_at_source": False}]
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


def test_create_extract_batch_duplicate_warning(auth_client, base_contract_key):
    payload = {
        "extracts": [
            {
                "month_ref": 5,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [
                    {"category": "rent", "description": "Aluguel", "amount": 1000.00, "is_credit": True, "is_withheld_at_source": False}
                ]
            }
        ]
    }
    first_res = auth_client.post("/extract-batches", json=payload)
    assert first_res.status_code == 201

    duplicate_res = auth_client.post("/extract-batches", json=payload)
    assert duplicate_res.status_code == 409
    error_detail = duplicate_res.json()["detail"]
    assert error_detail["code"] == "RM-0034"
    assert "translation" in error_detail
    assert "05/2026" in error_detail["translation"] or "5/2026" in error_detail["translation"]

def test_create_extract_batch_duplicate_confirmed(auth_client, base_contract_key):
    payload = {
        "extracts": [
            {
                "month_ref": 6,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [
                    {"category": "rent", "description": "Aluguel", "amount": 1200.00, "is_credit": True, "is_withheld_at_source": False}
                ]
            }
        ]
    }
    first_res = auth_client.post("/extract-batches", json=payload)
    assert first_res.status_code == 201

    confirmed_payload = {
        **payload,
        "confirm_duplicate": True
    }
    second_res = auth_client.post("/extract-batches", json=confirmed_payload)
    assert second_res.status_code == 201
    assert second_res.json()["key"] != first_res.json()["key"]

def test_create_extract_batch_intra_batch_duplicate(auth_client, base_contract_key):
    payload = {
        "extracts": [
            {
                "month_ref": 7,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [
                    {"category": "rent", "description": "Extrato 1", "amount": 1000.00, "is_credit": True, "is_withheld_at_source": False}
                ]
            },
            {
                "month_ref": 7,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [
                    {"category": "rent", "description": "Extrato 2", "amount": 1000.00, "is_credit": True, "is_withheld_at_source": False}
                ]
            }
        ]
    }
    res = auth_client.post("/extract-batches", json=payload)
    assert res.status_code == 409
    error_detail = res.json()["detail"]
    assert error_detail["code"] == "RM-0034"

def test_create_extract_batch_different_reference_or_contract(auth_client, base_contract_key):
    payload1 = {
        "extracts": [
            {
                "month_ref": 8,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [
                    {"category": "rent", "description": "Aluguel", "amount": 1000.00, "is_credit": True, "is_withheld_at_source": False}
                ]
            }
        ]
    }
    payload2 = {
        "extracts": [
            {
                "month_ref": 9,
                "year_ref": 2026,
                "contract_key": base_contract_key,
                "items": [
                    {"category": "rent", "description": "Aluguel", "amount": 1000.00, "is_credit": True, "is_withheld_at_source": False}
                ]
            }
        ]
    }
    res1 = auth_client.post("/extract-batches", json=payload1)
    assert res1.status_code == 201

    res2 = auth_client.post("/extract-batches", json=payload2)
    assert res2.status_code == 201
