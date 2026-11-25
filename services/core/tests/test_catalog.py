"""Tests for the catalog API against a real PostgreSQL (docs/09).

The database is created with infra's init scripts and migrated as core_owner;
the API runs as core_app, exactly as in Compose. Tokens are signed with a test
key and carry the permissions of each default profile (docs/06 D2).
"""

import os
import time
from collections.abc import Callable, Iterator
from pathlib import Path

import jwt
import pytest
from alembic import command
from alembic.config import Config
from almacen_security import TokenValidator
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from testcontainers.community.postgres import PostgresContainer

SERVICE_DIR = Path(__file__).resolve().parents[1]
INIT_DIR = SERVICE_DIR.parents[1] / "infra" / "postgres" / "init"
OWNER = ["catalog.manage", "price.edit", "cost.view", "location.manage", "stock.read"]
SELLER = ["stock.read", "customer.manage", "order.create"]
COURIER = ["stock.read", "dispatch.deliver"]
TABLES = (
    "audit_log, minimum_stock, price_tiers, presentations, products, locations, brands, categories"
)


@pytest.fixture(scope="module")
def database_urls(postgres_image) -> Iterator[dict[str, str]]:
    """PostgreSQL with infra's init scripts, migrated to the latest version."""
    container = (
        PostgresContainer(postgres_image, username="postgres", password="admin", driver="psycopg")
        .with_env("CORE_OWNER_PASSWORD", "owner")
        .with_env("CORE_APP_PASSWORD", "app")
        .with_env("AUTH_OWNER_PASSWORD", "auth-owner")
        .with_env("AUTH_APP_PASSWORD", "auth-app")
        .with_volume_mapping(str(INIT_DIR), "/docker-entrypoint-initdb.d", "ro")
    )
    with container as postgres:
        address = f"{postgres.get_container_host_ip()}:{postgres.get_exposed_port(5432)}"
        urls = {
            "owner": f"postgresql+psycopg://core_owner:owner@{address}/core_db",
            "app": f"postgresql+psycopg://core_app:app@{address}/core_db",
        }
        os.environ["MIGRATION_DATABASE_URL"] = urls["owner"]
        command.upgrade(Config(str(SERVICE_DIR / "alembic.ini")), "head")
        yield urls


@pytest.fixture(scope="module")
def private_key() -> rsa.RSAPrivateKey:
    """Test key pair standing in for auth's keys."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def client(database_urls, private_key, tmp_path) -> Iterator[TestClient]:
    """The core app running as core_app, with empty catalog tables."""
    from core.db import get_engine
    from core.main import app
    from core.security import get_token_validator

    owner_engine = create_engine(database_urls["owner"])
    with owner_engine.begin() as connection:
        connection.execute(text(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE"))
    owner_engine.dispose()

    key_path = tmp_path / "jwt_public.pem"
    key_path.write_bytes(
        private_key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    app_engine = create_engine(database_urls["app"])
    validator = TokenValidator(key_path, issuer="auth", audience="almacen")
    app.dependency_overrides[get_engine] = lambda: app_engine
    app.dependency_overrides[get_token_validator] = lambda: validator
    yield TestClient(app)
    app.dependency_overrides.clear()
    app_engine.dispose()


@pytest.fixture
def as_user(private_key) -> Callable[[list[str]], dict[str, str]]:
    """Return a function that gives the Authorization header of a user with those permissions."""

    def _headers(permissions: list[str]) -> dict[str, str]:
        now = int(time.time())
        claims = {
            "sub": "user-1",
            "name": "Usuario Ejemplo",
            "perms": permissions,
            "iss": "auth",
            "aud": "almacen",
            "iat": now,
            "exp": now + 900,
        }
        return {"Authorization": f"Bearer {jwt.encode(claims, private_key, algorithm='RS256')}"}

    return _headers


@pytest.fixture
def owner(as_user) -> dict[str, str]:
    """Headers of the owner (every catalog permission, including cost.view)."""
    return as_user(OWNER)


@pytest.fixture
def category_id(client, owner) -> int:
    """A category to attach products to."""
    return client.post("/v1/categories", json={"name": "Escritura"}, headers=owner).json()["id"]


def new_product(client, headers, category_id, **fields):
    """Create a product (a pencil by default) and return the response."""
    body = {"sku": "EJ-0001", "name": "Lapicero azul", "category_id": category_id,
            "base_unit": "unidad"} | fields  # fmt: skip
    return client.post("/v1/products", json=body, headers=headers)


# ---------- permissions (401 / 403) ----------


def test_catalog_needs_a_token(client):
    """Without a token every catalog endpoint answers 401."""
    assert client.get("/v1/products").status_code == 401
    assert client.get("/v1/categories").status_code == 401


def test_seller_cannot_create_products_or_change_prices(client, as_user, category_id):
    """A seller can read the catalog but not change it (403)."""
    seller = as_user(SELLER)

    assert client.get("/v1/products", headers=seller).status_code == 200
    assert new_product(client, seller, category_id).status_code == 403
    assert (
        client.put(
            "/v1/presentations/1/price-tiers", json={"tiers": []}, headers=seller
        ).status_code
        == 403
    )


def test_support_lists_only_need_a_session(client, as_user, category_id):
    """Categories and locations can be read by any logged-in user (docs/06 D2)."""
    courier = as_user(COURIER)

    assert client.get("/v1/categories", headers=courier).json()[0]["name"] == "Escritura"
    assert client.get("/v1/locations", headers=courier).status_code == 200


# ---------- categories, brands and locations ----------


def test_category_names_do_not_repeat_regardless_of_case(client, owner, category_id):
    """'escritura' clashes with 'Escritura' (409)."""
    response = client.post("/v1/categories", json={"name": " escritura "}, headers=owner)

    assert response.status_code == 409


def test_location_type_must_be_store_or_warehouse(client, owner):
    """Only STORE or WAREHOUSE are valid (422)."""
    ok = client.post("/v1/locations", json={"name": "Tienda 1", "type": "STORE"}, headers=owner)
    bad = client.post("/v1/locations", json={"name": "Otra", "type": "OFICINA"}, headers=owner)

    assert ok.status_code == 201
    assert bad.status_code == 422


def test_required_fields_cannot_be_cleared(client, owner, category_id):
    """PATCH with name=null is rejected instead of leaving a nameless category."""
    response = client.patch(f"/v1/categories/{category_id}", json={"name": None}, headers=owner)

    assert response.status_code == 422


# ---------- products and cost ----------


def test_new_product_gets_its_base_presentation(client, owner, category_id):
    """Creating a product also creates its base presentation with factor 1 (docs/09)."""
    response = new_product(client, owner, category_id)

    assert response.status_code == 201
    product = response.json()
    assert product["base_unit"] == "UNIDAD"
    assert [(p["name"], p["factor"]) for p in product["presentations"]] == [("UNIDAD", 1)]


def test_cost_is_hidden_without_cost_view(client, owner, as_user, category_id):
    """The owner sees the cost; a seller does not even get the field (RNF-14)."""
    product_id = new_product(client, owner, category_id, cost="0.45").json()["id"]

    seen_by_owner = client.get(f"/v1/products/{product_id}", headers=owner).json()
    seen_by_seller = client.get(f"/v1/products/{product_id}", headers=as_user(SELLER)).json()

    assert seen_by_owner["cost"] == "0.45"
    assert "cost" not in seen_by_seller


def test_sending_a_cost_needs_cost_view(client, as_user, category_id):
    """catalog.manage alone cannot set the cost (403)."""
    manager = as_user(["catalog.manage", "stock.read"])

    assert new_product(client, manager, category_id, cost="1.00").status_code == 403
    assert new_product(client, manager, category_id).status_code == 201


def test_sku_does_not_repeat_regardless_of_case(client, owner, category_id):
    """'ej-0001' clashes with 'EJ-0001' (409)."""
    new_product(client, owner, category_id)

    assert new_product(client, owner, category_id, sku="ej-0001").status_code == 409


def test_a_barcode_points_to_one_thing_only(client, owner, category_id):
    """A presentation cannot reuse a product's barcode (409): a scan must be unambiguous."""
    product_id = new_product(client, owner, category_id, barcode="7750000000017").json()["id"]

    response = client.post(
        f"/v1/products/{product_id}/presentations",
        json={"name": "caja", "factor": 12, "barcode": "7750000000017"},
        headers=owner,
    )

    assert response.status_code == 409


def test_search_by_name_sku_or_barcode(client, owner, category_id):
    """Name matches partially; SKU and barcode match exactly. The total is returned."""
    new_product(client, owner, category_id, barcode="7750000000017")
    new_product(client, owner, category_id, sku="EJ-0002", name="Cuaderno A4")

    by_name = client.get("/v1/products", params={"q": "lapi"}, headers=owner).json()
    by_sku = client.get("/v1/products", params={"q": "ej-0002"}, headers=owner).json()
    by_barcode = client.get("/v1/products", params={"q": "7750000000017"}, headers=owner).json()
    page = client.get("/v1/products", params={"limit": 1}, headers=owner).json()

    assert [p["sku"] for p in by_name["items"]] == ["EJ-0001"]
    assert [p["sku"] for p in by_sku["items"]] == ["EJ-0002"]
    assert [p["sku"] for p in by_barcode["items"]] == ["EJ-0001"]
    assert page["total"] == 2
    assert len(page["items"]) == 1


# ---------- presentations and prices ----------


def test_presentation_factor_cannot_be_changed(client, owner, category_id):
    """Sending a factor when editing a presentation is rejected (422), not ignored."""
    product = new_product(client, owner, category_id).json()
    presentation_id = product["presentations"][0]["id"]

    response = client.patch(
        f"/v1/presentations/{presentation_id}", json={"factor": 12}, headers=owner
    )

    assert response.status_code == 422


def test_base_presentation_cannot_be_deactivated(client, owner, category_id):
    """Without the factor-1 presentation the product could not be sold by unit (422)."""
    product = new_product(client, owner, category_id).json()
    base_id = product["presentations"][0]["id"]

    response = client.patch(f"/v1/presentations/{base_id}", json={"active": False}, headers=owner)

    assert response.status_code == 422


def test_price_tiers_need_a_price_from_one(client, owner, category_id):
    """Every presentation needs a price from quantity 1 (docs/03 rule 6)."""
    base_id = new_product(client, owner, category_id).json()["presentations"][0]["id"]
    tiers = {"tiers": [{"min_quantity": 12, "price": "0.90"}]}

    response = client.put(f"/v1/presentations/{base_id}/price-tiers", json=tiers, headers=owner)

    assert response.status_code == 422


def test_price_change_is_saved_and_audited(client, owner, category_id, database_urls):
    """The new tiers replace the old ones, and the audit log keeps both."""
    base_id = new_product(client, owner, category_id).json()["presentations"][0]["id"]
    url = f"/v1/presentations/{base_id}/price-tiers"
    client.put(url, json={"tiers": [{"min_quantity": 1, "price": "1.00"}]}, headers=owner)

    response = client.put(
        url,
        json={
            "tiers": [{"min_quantity": 12, "price": "0.90"}, {"min_quantity": 1, "price": "1.10"}]
        },
        headers=owner,
    )

    tiers = response.json()["presentations"][0]["price_tiers"]
    assert [(t["min_quantity"], t["price"]) for t in tiers] == [(1, "1.10"), (12, "0.90")]
    engine = create_engine(database_urls["owner"])
    with engine.connect() as connection:
        before, after, user_name = connection.execute(
            text("SELECT before, after, user_name FROM audit_log "
                 "WHERE action = 'price_tiers.replace' ORDER BY id DESC LIMIT 1")
        ).one()  # fmt: skip
    engine.dispose()
    assert before == {"tiers": [[1, "1.00"]]}
    assert after == {"tiers": [[1, "1.10"], [12, "0.90"]]}
    assert user_name == "Usuario Ejemplo"


# ---------- minimum stock and audit log ----------


def test_minimum_stock_per_location(client, owner, category_id):
    """A threshold can be set for an active location; an unknown one answers 404."""
    product_id = new_product(client, owner, category_id).json()["id"]
    location_id = client.post(
        "/v1/locations", json={"name": "Almacén 1", "type": "WAREHOUSE"}, headers=owner
    ).json()["id"]
    url = f"/v1/products/{product_id}/minimum-stock"

    assert (
        client.put(f"{url}/{location_id}", json={"quantity": 24}, headers=owner).status_code == 204
    )
    assert client.put(f"{url}/999", json={"quantity": 24}, headers=owner).status_code == 404


def test_audit_log_cannot_be_changed_by_the_application(client, owner, category_id, database_urls):
    """core_app can add audit entries but not modify or delete them (RNF-05)."""
    new_product(client, owner, category_id)
    engine = create_engine(database_urls["app"])

    with engine.begin() as connection, pytest.raises(ProgrammingError, match="permission denied"):
        connection.execute(text("UPDATE audit_log SET user_name = 'otro'"))
    with engine.begin() as connection, pytest.raises(ProgrammingError, match="permission denied"):
        connection.execute(text("DELETE FROM audit_log"))
    engine.dispose()
