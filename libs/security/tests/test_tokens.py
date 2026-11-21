"""Tests for TokenValidator: every way a token can be wrong is rejected (ADR-0007)."""

import base64
import hashlib
import hmac
import json
import time

import pytest
from conftest import AUDIENCE, ISSUER

from almacen_security import InvalidTokenError, TokenValidator


def build_unverified_token(header: dict, payload: dict, hmac_secret: bytes | None = None) -> str:
    """Assemble a JWT by hand (base64 parts joined by dots).

    PyJWT refuses to create the tokens an attacker would send, so these tests
    build them directly to check that the validator rejects them.
    """

    def encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    signing_input = f"{encode(json.dumps(header).encode())}.{encode(json.dumps(payload).encode())}"
    signature = b""
    if hmac_secret is not None:
        signature = hmac.new(hmac_secret, signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{encode(signature)}"


def unauthorized_claims() -> dict:
    """Claims that are fine in themselves; only the signature makes the token invalid."""
    now = int(time.time())
    return {
        "sub": "user-2",
        "name": "Sin firma valida",
        "perms": ["user.manage"],
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + 900,
    }


@pytest.fixture
def validator(public_key_path) -> TokenValidator:
    """A validator configured like a service: auth's public key, issuer and audience."""
    return TokenValidator(public_key_path, issuer=ISSUER, audience=AUDIENCE)


def test_valid_token_returns_its_claims(validator, make_token):
    """A correct token gives the user id, name and permissions."""
    claims = validator.validate(make_token())

    assert claims.user_id == "user-1"
    assert claims.name == "Usuario Ejemplo"
    assert claims.has("order.create")
    assert not claims.has("price.edit")


def test_expired_token_is_rejected(validator, make_token):
    """A token past its exp (15 minutes) is rejected."""
    past = int(time.time()) - 60
    with pytest.raises(InvalidTokenError):
        validator.validate(make_token(iat=past - 900, exp=past))


def test_token_signed_with_another_key_is_rejected(validator, make_token, other_private_key):
    """A token not signed by auth's private key is rejected."""
    with pytest.raises(InvalidTokenError):
        validator.validate(make_token(key=other_private_key))


def test_token_for_another_audience_is_rejected(validator, make_token):
    """A token issued for another system (aud) is rejected."""
    with pytest.raises(InvalidTokenError):
        validator.validate(make_token(aud="otro-sistema"))


def test_token_from_another_issuer_is_rejected(validator, make_token):
    """A token not issued by auth (iss) is rejected."""
    with pytest.raises(InvalidTokenError):
        validator.validate(make_token(iss="impostor"))


def test_unsigned_token_is_rejected(validator):
    """alg "none" (no signature at all) is rejected: the algorithm is fixed to RS256."""
    token = build_unverified_token({"alg": "none", "typ": "JWT"}, unauthorized_claims())

    with pytest.raises(InvalidTokenError):
        validator.validate(token)


def test_hs256_token_signed_with_public_key_is_rejected(validator, public_key_path):
    """Algorithm confusion: HS256 with the public key used as the secret must fail."""
    token = build_unverified_token(
        {"alg": "HS256", "typ": "JWT"}, unauthorized_claims(), public_key_path.read_bytes()
    )

    with pytest.raises(InvalidTokenError):
        validator.validate(token)


def test_token_without_permissions_claim_is_rejected(validator, make_token):
    """Every required claim must be present (here perms is removed)."""
    with pytest.raises(InvalidTokenError):
        validator.validate(make_token(perms=None))


def test_permissions_must_be_a_list_of_codes(validator, make_token):
    """perms with the wrong type is rejected instead of being misread."""
    with pytest.raises(InvalidTokenError):
        validator.validate(make_token(perms="order.create"))
