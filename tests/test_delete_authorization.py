import pytest


DELETE_PATHS = [
    "/tenants/missing-tenant",
    "/owners/missing-owner",
    "/properties/missing-property",
    "/real-estates/missing-real-estate",
    "/guarantees/missing-guarantee",
    "/contracts/missing-contract",
    "/payments/missing-payment",
    "/extract-batches/missing-batch",
    "/extract-batches/missing-batch/extracts/missing-extract",
]


@pytest.mark.parametrize("path", DELETE_PATHS)
def test_delete_route_allows_master_to_reach_handler(auth_client, path):
    response = auth_client.delete(path)

    assert response.status_code == 404


@pytest.mark.parametrize("path", DELETE_PATHS)
def test_delete_route_rejects_non_master(non_master_client, path):
    response = non_master_client.delete(path)

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "RM-0020"


@pytest.mark.parametrize("path", DELETE_PATHS)
def test_delete_route_rejects_missing_credentials(client, path):
    response = client.delete(path)

    assert response.status_code == 401


def test_delete_route_rejects_master_token_after_role_demotion(demoted_master_client):
    response = demoted_master_client.delete("/owners/missing-owner")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "RM-0020"
