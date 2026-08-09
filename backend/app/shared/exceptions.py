class DomainError(Exception):
    """Base class for all domain errors.

    Carries an error_code used by the HTTP error handler to build the response body.
    """

    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class ValidationError(DomainError):
    """An invariant was violated or input failed domain-level validation."""

    def __init__(
        self, error_code: str = "VALIDATION_ERROR", message: str = "Invalid input."
    ) -> None:
        super().__init__(error_code, message)


class NotFoundError(DomainError):
    """The requested entity does not exist."""

    def __init__(self, error_code: str = "NOT_FOUND", message: str = "Resource not found.") -> None:
        super().__init__(error_code, message)


class ConflictError(DomainError):
    """A duplicate or conflicting entity already exists."""

    def __init__(
        self, error_code: str = "CONFLICT", message: str = "Resource already exists."
    ) -> None:
        super().__init__(error_code, message)


class PermissionError(DomainError):
    """Authentication or authorisation failure."""

    def __init__(self, error_code: str = "FORBIDDEN", message: str = "Permission denied.") -> None:
        super().__init__(error_code, message)


class LastAdministratorError(DomainError):
    """Action would remove the last administrator account."""

    def __init__(self) -> None:
        super().__init__(
            error_code="LAST_ADMINISTRATOR",
            message="Cannot remove the last administrator account.",
        )
