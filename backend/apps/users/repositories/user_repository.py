"""Repository layer — abstracts data access for User entities."""

from typing import List, Optional

from apps.users.models import User


class UserRepository:
    """Thin wrapper around the Django ORM for User operations."""

    def find_by_email(self, email: str) -> Optional[User]:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def insert(self, email: str, password: str) -> User:
        return User.objects.create(email=email, password=password)

    def list_all(self) -> List[User]:
        return list(User.objects.all().order_by("email"))

    def clear(self) -> None:
        User.objects.all().delete()
