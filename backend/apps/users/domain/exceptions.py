"""Domain-level exceptions for the users bounded context."""


class InvalidUserInput(Exception):
    """Raised when email or password are empty after normalization."""

    pass


class UserAlreadyExists(Exception):
    """Raised when attempting to register a duplicate email."""

    pass


class InvalidCredentials(Exception):
    """Raised when login credentials do not match."""

    pass
