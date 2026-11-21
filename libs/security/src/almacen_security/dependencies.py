"""FastAPI dependencies that protect endpoints with the access token."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from almacen_security.tokens import InvalidTokenError, TokenClaims, TokenValidator

# auto_error=False: a missing token is answered by us with the same 401 as an
# invalid one, instead of FastAPI's default 403.
_bearer = HTTPBearer(auto_error=False)
_UNAUTHORIZED_HEADERS = {"WWW-Authenticate": "Bearer"}


class TokenGuard:
    """Build FastAPI dependencies that require a valid token and, optionally, a permission.

    A service creates one guard at startup and uses it on its endpoints:

        guard = TokenGuard(get_validator)

        @app.get("/v1/orders")
        def list_orders(user: Annotated[TokenClaims, Depends(guard.require("order.read"))]):
            ...
    """

    def __init__(self, get_validator: Callable[[], TokenValidator]) -> None:
        """Remember how to obtain the validator (a dependency, so tests can replace it)."""
        self._get_validator = get_validator

    def current_user(self) -> Callable[..., TokenClaims]:
        """Dependency: the claims of a valid token, or 401 (docs/06 D1.10, A01 and A07)."""
        get_validator = self._get_validator

        def dependency(
            credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
            validator: Annotated[TokenValidator, Depends(get_validator)],
        ) -> TokenClaims:
            if credentials is None:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Not authenticated", _UNAUTHORIZED_HEADERS
                )
            try:
                return validator.validate(credentials.credentials)
            except InvalidTokenError:
                # Same message for every reason: do not tell an attacker what failed.
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, "Invalid token", _UNAUTHORIZED_HEADERS
                ) from None

        return dependency

    def require(self, permission: str) -> Callable[..., TokenClaims]:
        """Dependency: a valid token that includes the permission, else 401 or 403."""
        current_user = self.current_user()

        def dependency(user: Annotated[TokenClaims, Depends(current_user)]) -> TokenClaims:
            if not user.has(permission):
                raise HTTPException(status.HTTP_403_FORBIDDEN, "Missing permission")
            return user

        return dependency
