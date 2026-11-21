"""Access control of the core service, built on the shared almacen_security library (T-11)."""

from functools import lru_cache

from almacen_security import TokenGuard, TokenValidator

from core.config import get_settings


@lru_cache
def get_token_validator() -> TokenValidator:
    """Create the token validator once, with auth's public key and the expected iss/aud."""
    settings = get_settings()
    return TokenValidator(
        settings.jwt_public_key_path,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )


# Endpoints use guard.current_user() (any valid token) or guard.require("perm.code").
guard = TokenGuard(get_token_validator)
