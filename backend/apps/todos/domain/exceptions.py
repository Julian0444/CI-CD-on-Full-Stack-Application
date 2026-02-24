"""Domain-level exceptions for the todos bounded context."""


class InvalidTodoInput(Exception):
    """Raised when required todo fields are missing or empty."""

    pass


class InvalidTodoID(Exception):
    """Raised when the provided todo ID is not a valid UUID."""

    pass


class TodoNotFound(Exception):
    """Raised when the requested todo does not exist."""

    pass
