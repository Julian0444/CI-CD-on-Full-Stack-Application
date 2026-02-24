"""
Business logic for todo operations.

All validation and normalization lives here — views are thin.
"""

import uuid
from typing import Dict, List, Optional

from apps.todos.domain.exceptions import InvalidTodoID, InvalidTodoInput, TodoNotFound
from apps.todos.repositories.todo_repository import TodoRepository


def _normalize_email(email: str) -> str:
    return email.strip().lower() if email else ""


def _normalize_text(value: str) -> str:
    return value.strip() if value else ""


def _parse_uuid(value: str) -> uuid.UUID:
    """Parse a string as UUID. Raises InvalidTodoID on failure."""
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError):
        raise InvalidTodoID()


def _todo_to_response(todo) -> Dict:
    """Convert a Todo model instance to the API response format."""
    return {
        "id": str(todo.id),
        "email": todo.email,
        "title": todo.title,
        "completed": todo.completed,
        "createdAt": (
            todo.created_at.isoformat().replace("+00:00", "Z")
            if todo.created_at
            else None
        ),
    }


class TodoService:
    def __init__(self, repo: Optional[TodoRepository] = None):
        self.repo = repo or TodoRepository()

    def list(self, email: str = "") -> List[Dict]:
        email = _normalize_email(email)
        todos = self.repo.list(email)
        return [_todo_to_response(t) for t in todos]

    def create(self, email: str, title: str) -> Dict:
        email = _normalize_email(email)
        title = _normalize_text(title)

        if not email or not title:
            raise InvalidTodoInput()

        todo = self.repo.create(email=email, title=title)
        return _todo_to_response(todo)

    def update(
        self,
        todo_id: str,
        title: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> Dict:
        if title is None and completed is None:
            raise InvalidTodoInput()

        parsed_id = _parse_uuid(todo_id)

        if title is not None:
            title = _normalize_text(title)
            if not title:
                raise InvalidTodoInput()

        todo = self.repo.get_by_id(parsed_id)
        if todo is None:
            raise TodoNotFound()

        updated = self.repo.update(todo, title=title, completed=completed)
        return _todo_to_response(updated)

    def delete(self, todo_id: str) -> None:
        parsed_id = _parse_uuid(todo_id)
        todo = self.repo.get_by_id(parsed_id)
        if todo is None:
            raise TodoNotFound()
        self.repo.delete(todo)

    def clear(self, email: str = "") -> None:
        email = _normalize_email(email)
        self.repo.clear(email)
