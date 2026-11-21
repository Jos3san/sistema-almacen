"""Shared security for the services: access token validation and permission checks.

auth signs access tokens with its private key (RS256); every service validates
them with the public key, read from a mounted file, without calling auth
(ADR-0007, docs/06 D1.3).
"""

from almacen_security.dependencies import TokenGuard
from almacen_security.tokens import InvalidTokenError, TokenClaims, TokenValidator

__all__ = ["InvalidTokenError", "TokenClaims", "TokenGuard", "TokenValidator"]
