"""Domain exceptions.

Services raise these protocol-agnostic exceptions; controllers are
responsible for catching them and translating to the appropriate HTTP
response.
"""


class AppError(Exception):
    """Base class for all domain exceptions."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""


class ForbiddenError(AppError):
    """Raised when the current user lacks permission for an action."""


class ConflictError(AppError):
    """Raised when a resource already exists (e.g. duplicate username)."""


class UnauthorizedError(AppError):
    """Raised when authentication credentials are invalid or missing."""
