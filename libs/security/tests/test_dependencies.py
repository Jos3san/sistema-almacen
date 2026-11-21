"""Tests for TokenGuard on a small FastAPI app: 401 and 403 answers (docs/06 D1.10, A01)."""

from typing import Annotated

import pytest
from conftest import AUDIENCE, ISSUER
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from almacen_security import TokenClaims, TokenGuard, TokenValidator


@pytest.fixture
def client(public_key_path) -> TestClient:
    """An app with one endpoint that needs a login and one that needs order.create."""
    validator = TokenValidator(public_key_path, issuer=ISSUER, audience=AUDIENCE)
    guard = TokenGuard(lambda: validator)
    app = FastAPI()

    @app.get("/me")
    def me(user: Annotated[TokenClaims, Depends(guard.current_user())]) -> dict[str, str]:
        return {"user_id": user.user_id}

    @app.post("/orders")
    def create_order(user: Annotated[TokenClaims, Depends(guard.require("order.create"))]):
        return {"created_by": user.user_id}

    @app.put("/prices")
    def edit_price(user: Annotated[TokenClaims, Depends(guard.require("price.edit"))]):
        return {"edited_by": user.user_id}

    return TestClient(app)


def bearer(token: str) -> dict[str, str]:
    """Authorization header with the token."""
    return {"Authorization": f"Bearer {token}"}


def test_no_token_is_401(client):
    """Without a token: 401 and a WWW-Authenticate header."""
    response = client.get("/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_invalid_token_is_401_with_generic_message(client, make_token):
    """A bad token gets 401 and a message that does not say why."""
    response = client.get("/me", headers=bearer(make_token(aud="otro-sistema")))

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_valid_token_is_200(client, make_token):
    """A valid token reaches the endpoint, which knows who the user is."""
    response = client.get("/me", headers=bearer(make_token()))

    assert response.status_code == 200
    assert response.json() == {"user_id": "user-1"}


def test_with_permission_is_200(client, make_token):
    """A user with the permission passes."""
    response = client.post("/orders", headers=bearer(make_token()))

    assert response.status_code == 200


def test_without_permission_is_403(client, make_token):
    """A logged-in user without the permission gets 403, not 401."""
    response = client.put("/prices", headers=bearer(make_token()))

    assert response.status_code == 403


def test_permission_check_still_requires_a_valid_token(client):
    """An endpoint with a permission also answers 401 when there is no token."""
    assert client.post("/orders").status_code == 401
