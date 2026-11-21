"""Validation of access tokens (JWT signed with RS256 by auth)."""

from dataclasses import dataclass
from pathlib import Path

import jwt

# Only RS256 is accepted. Never read the algorithm from the token itself:
# that would allow "none" or HS256 tokens forged with the public key
# (OWASP A08, docs/06 D1.10).
ALGORITHM = "RS256"
REQUIRED_CLAIMS = ["sub", "name", "perms", "iss", "aud", "iat", "exp"]


class InvalidTokenError(Exception):
    """The token is missing, expired, badly signed or meant for someone else."""


@dataclass(frozen=True)
class TokenClaims:
    """What a valid access token says about the user (docs/06 D1.3)."""

    user_id: str
    name: str
    permissions: frozenset[str]

    def has(self, permission: str) -> bool:
        """Tell whether the user has the permission code, e.g. "order.create"."""
        return permission in self.permissions


class TokenValidator:
    """Check access tokens with auth's public key.

    The key is read once from a file mounted in the container
    (JWT_PUBLIC_KEY_PATH), so services validate tokens even when auth is down.
    """

    def __init__(self, public_key_path: Path, issuer: str, audience: str) -> None:
        """Load the public key and remember who must have issued the tokens and for whom."""
        self._public_key = Path(public_key_path).read_text(encoding="utf-8")
        self._issuer = issuer
        self._audience = audience

    def validate(self, token: str) -> TokenClaims:
        """Return the token's claims, or raise InvalidTokenError if anything is wrong.

        Checks the RS256 signature, the issuer (iss), the audience (aud), the
        expiry (exp) and that every required claim is present.
        """
        try:
            payload = jwt.decode(
                token,
                self._public_key,
                algorithms=[ALGORITHM],
                issuer=self._issuer,
                audience=self._audience,
                options={"require": REQUIRED_CLAIMS},
            )
        except jwt.PyJWTError as error:
            raise InvalidTokenError(str(error)) from error

        permissions = payload["perms"]
        if not isinstance(permissions, list) or not all(isinstance(p, str) for p in permissions):
            raise InvalidTokenError("perms must be a list of permission codes")
        return TokenClaims(
            user_id=str(payload["sub"]),
            name=str(payload["name"]),
            permissions=frozenset(permissions),
        )
