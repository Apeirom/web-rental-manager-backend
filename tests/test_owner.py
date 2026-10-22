from src.models import ExtractBatchModel, ExtractModel


def test_create_owner(auth_client):
    payload = {
        "name": "Carlos Silva",
        "document_number": "52998224725"
    }
    response = auth_client.post("/owners", json=payload)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Carlos Silva"
    assert response.json()["document_number"] == "529.982.247-25"
    assert "key" in response.json()
    assert "id" not in response.json()

def test_get_all_owners(auth_client):
    # Garantir que existe pelo menos um
    auth_client.post("/owners", json={"name": "Ana Paula", "document_number": "98765432100"})
    
    response = auth_client.get("/owners")
    
    assert response.status_code == 200
    res_json = response.json()
    assert "total" in res_json
    assert "skip" in res_json
    assert "limit" in res_json
    assert isinstance(res_json["data"], list)
    assert len(res_json["data"]) > 0

def test_get_owner_by_key(auth_client):
    payload = {"name": "Marcos Silva"}
    create_res = auth_client.post("/owners", json=payload)
    owner_key = create_res.json()["key"]

    response = auth_client.get(f"/owners/{owner_key}")
    assert response.status_code == 200
    assert response.json()["name"] == "Marcos Silva"
    assert response.json()["key"] == owner_key

def test_get_owner_not_found(auth_client):
    response = auth_client.get("/owners/invalid-uuid-key")
    assert response.status_code == 404
    # Ajuste o código do erro ("RM-XXXX") conforme o mapeamento do seu OwnerNotFoundError
    assert "detail" in response.json() 

def test_update_owner(auth_client):
    payload = {"name": "João Antigo", "document_number": "529.982.247-25"}
    create_res = auth_client.post("/owners", json=payload)
    owner_key = create_res.json()["key"]

    update_payload = {"name": "João Novo", "document_number": "111.444.777-35"}
    update_res = auth_client.put(f"/owners/{owner_key}", json=update_payload)
    
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "João Novo"
    assert update_res.json()["document_number"] == "111.444.777-35"

def test_delete_owner(auth_client):
    payload = {"name": "Para Deletar"}
    create_res = auth_client.post("/owners", json=payload)
    owner_key = create_res.json()["key"]

    delete_res = auth_client.delete(f"/owners/{owner_key}")
    assert delete_res.status_code == 204

    get_res = auth_client.get(f"/owners/{owner_key}")
    assert get_res.status_code == 404


def test_delete_owner_preserves_properties_and_contract_data(
    auth_client,
    owner_factory,
    property_factory,
    tenant_factory,
    contract_factory,
    extract_batch_factory,
    payment_factory,
    db_session,
):
    owner = owner_factory(name="Owner to delete")
    owned_property = property_factory(
        owner_key=owner["key"],
        property_name="Owned Property",
    )
    owned_tenant = tenant_factory(
        name="Owned Tenant",
        document_number="100.000.000-19",
    )
    owned_contract = contract_factory(
        payload={
            "property_key": owned_property["key"],
            "tenant_key": owned_tenant["key"],
            "rent_amount": 1000.00,
        }
    )

    unrelated_property = property_factory(property_name="Unrelated Property")
    unrelated_tenant = tenant_factory(
        name="Unrelated Tenant",
        document_number="100.000.001-08",
    )
    unrelated_contract = contract_factory(
        payload={
            "property_key": unrelated_property["key"],
            "tenant_key": unrelated_tenant["key"],
            "rent_amount": 500.00,
        }
    )

    single_extract_batch = extract_batch_factory(
        extracts=[
            {
                "month_ref": 1,
                "year_ref": 2026,
                "contract_key": owned_contract["key"],
                "items": [
                    {
                        "category": "rent",
                        "description": "Owned rent credit",
                        "amount": 1000.00,
                        "is_credit": True,
                        "is_withheld_at_source": False,
                    },
                    {
                        "category": "water",
                        "description": "Owned rent debit",
                        "amount": 1000.00,
                        "is_credit": False,
                        "is_withheld_at_source": False,
                    },
                ],
            }
        ]
    )
    single_batch_payment = payment_factory(
        payment_date="2026-01-10",
        amount=1000.00,
        extract_batch_key=single_extract_batch["key"],
        link=True,
    )

    mixed_extract_batch = extract_batch_factory(
        extracts=[
            {
                "month_ref": 2,
                "year_ref": 2026,
                "contract_key": owned_contract["key"],
                "items": [
                    {
                        "category": "rent",
                        "description": "Owned rent",
                        "amount": 1000.00,
                        "is_credit": True,
                        "is_withheld_at_source": False,
                    }
                ],
            },
            {
                "month_ref": 2,
                "year_ref": 2026,
                "contract_key": unrelated_contract["key"],
                "items": [
                    {
                        "category": "rent",
                        "description": "Unrelated rent",
                        "amount": 500.00,
                        "is_credit": True,
                        "is_withheld_at_source": False,
                    }
                ],
            },
        ]
    )
    mixed_batch_payment = payment_factory(
        payment_date="2026-02-10",
        amount=500.00,
        extract_batch_key=mixed_extract_batch["key"],
        link=True,
    )

    response = auth_client.delete(f"/owners/{owner['key']}")

    assert response.status_code == 204
    assert auth_client.get(f"/owners/{owner['key']}").status_code == 404
    property_response = auth_client.get(f"/properties/{owned_property['key']}")
    assert property_response.status_code == 200
    assert property_response.json()["equity_participations"] == []
    assert auth_client.get(f"/contracts/{owned_contract['key']}").status_code == 200

    preserved_single_batch = (
        db_session.query(ExtractBatchModel)
        .filter(ExtractBatchModel.key == single_extract_batch["key"])
        .first()
    )
    assert preserved_single_batch is not None
    single_extracts = (
        db_session.query(ExtractModel)
        .filter(ExtractModel.extract_batch_id == preserved_single_batch.id)
        .all()
    )
    assert len(single_extracts) == 1
    assert single_extracts[0].contract.key == owned_contract["key"]

    preserved_batch = (
        db_session.query(ExtractBatchModel)
        .filter(ExtractBatchModel.key == mixed_extract_batch["key"])
        .first()
    )
    assert preserved_batch is not None
    surviving_extracts = (
        db_session.query(ExtractModel)
        .filter(ExtractModel.extract_batch_id == preserved_batch.id)
        .all()
    )
    assert len(surviving_extracts) == 2
    assert {extract.contract.key for extract in surviving_extracts} == {
        owned_contract["key"],
        unrelated_contract["key"],
    }

    assert auth_client.get(
        f"/properties/{unrelated_property['key']}"
    ).status_code == 200
    assert auth_client.get(
        f"/contracts/{unrelated_contract['key']}"
    ).status_code == 200

    for payment in (single_batch_payment, mixed_batch_payment):
        payment_response = auth_client.get(f"/payments/{payment['key']}")
        assert payment_response.status_code == 200
        assert payment_response.json()["status"] == "linked"
        assert payment_response.json()["extract_batch_key"] is not None


def test_delete_property_preserves_its_owner(
    auth_client, owner_factory, property_factory
):
    owner = owner_factory(name="Owner stays")
    property_record = property_factory(
        owner_key=owner["key"],
        property_name="Property removed",
    )

    response = auth_client.delete(f"/properties/{property_record['key']}")

    assert response.status_code == 204
    owner_response = auth_client.get(f"/owners/{owner['key']}")
    assert owner_response.status_code == 200
    assert owner_response.json()["name"] == "Owner stays"


def test_delete_owner_preserves_property_with_another_owner(
    auth_client, owner_factory, property_factory
):
    owner_to_delete = owner_factory(name="Owner to remove")
    surviving_owner = owner_factory(name="Surviving owner")
    property_record = property_factory(
        property_name="Shared property",
        equity_participations=[
            {
                "owner_key": owner_to_delete["key"],
                "participation_percentage": 50,
            },
            {
                "owner_key": surviving_owner["key"],
                "participation_percentage": 25,
            },
        ],
    )

    response = auth_client.delete(f"/owners/{owner_to_delete['key']}")

    assert response.status_code == 204
    property_response = auth_client.get(f"/properties/{property_record['key']}")
    assert property_response.status_code == 200
    remaining = property_response.json()["equity_participations"]
    assert len(remaining) == 1
    assert remaining[0]["owner"]["key"] == surviving_owner["key"]
    assert remaining[0]["participation_percentage"] == 25