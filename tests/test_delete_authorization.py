import pytest

from src.models import UserModel
from src.utils.security import create_access_token


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
def test_delete_route_rejects_non_master(auth_client, db_session, path):
    user = UserModel(
        key="non-master-user",
        name="Regular User",
        email="regular@example.com",
        role="user",
        hashed_password="unused",
    )
    db_session.add(user)
    db_session.commit()

    token = create_access_token(
        {"key": user.key, "email": user.email, "role": user.role}
    )
    auth_client.headers["Authorization"] = f"Bearer {token}"

    response = auth_client.delete(path)

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "RM-0020"


@pytest.mark.parametrize("path", DELETE_PATHS)
def test_delete_route_rejects_missing_credentials(client, path):
    response = client.delete(path)

    assert response.status_code == 401


def test_delete_route_rejects_master_token_after_role_demotion(
    auth_client, db_session
):
    user = UserModel(
        key="demoted-master",
        name="Demoted Master",
        email="demoted@example.com",
        role="user",
        hashed_password="unused",
    )
    db_session.add(user)
    db_session.commit()

    token = create_access_token(
        {"key": user.key, "email": user.email, "role": "master"}
    )
    auth_client.headers["Authorization"] = f"Bearer {token}"

    response = auth_client.delete("/owners/missing-owner")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "RM-0020"
