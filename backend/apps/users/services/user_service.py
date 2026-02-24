"""
Business logic for user operations.

All validation and normalization lives here — views are thin.
"""

from typing import Dict, List, Optional

from apps.users.domain.exceptions import (
    InvalidCredentials,
    InvalidUserInput,
    UserAlreadyExists,
)
from apps.users.repositories.user_repository import UserRepository


def _normalize_email(email: str) -> str:
    return email.strip().lower() if email else ""


def _normalize_text(value: str) -> str:
    return value.strip() if value else ""


class UserService:
    def __init__(self, repo: Optional[UserRepository] = None):
        self.repo = repo or UserRepository()

    def register(self, email: str, password: str) -> None:
        """Register a new user. Raises domain exceptions on failure."""
        email = _normalize_email(email)
        password = _normalize_text(password)

        if not email or not password:
            raise InvalidUserInput()

        existing = self.repo.find_by_email(email)
        if existing is not None:
            raise UserAlreadyExists()

        self.repo.insert(email=email, password=password)

    def login(self, email: str, password: str) -> None:
        """Validate credentials. Raises InvalidCredentials on failure."""
        email = _normalize_email(email)
        password = _normalize_text(password)

        if not email or not password:
            raise InvalidCredentials()

        user = self.repo.find_by_email(email)
        if user is None or user.password != password:
            raise InvalidCredentials()

    def list_users(self) -> List[Dict[str, str]]:
        """Return all users in their public representation (email only)."""
        users = self.repo.list_all()
        return [{"email": u.email} for u in users]

    def clear(self) -> None:
        """Remove all users."""
        self.repo.clear()
