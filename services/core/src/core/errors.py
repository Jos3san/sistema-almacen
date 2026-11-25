"""Domain errors: services raise them, main.py turns them into HTTP answers (docs/06 D1.11).

Their messages are written by us for the user, so they never leak internal details.
"""


class DomainError(Exception):
    """Base class of every expected business error."""


class NotFoundError(DomainError):
    """The requested record does not exist (404)."""


class ConflictError(DomainError):
    """The change clashes with existing data, e.g. a repeated SKU (409)."""


class BusinessRuleError(DomainError):
    """The change breaks a business rule of docs/03 or docs/09 (422)."""
