"""Repository layer — abstracts data access for Todo entities."""

import uuid
from typing import List, Optional

from apps.todos.models import Todo


class TodoRepository:
    """Thin wrapper around the Django ORM for Todo operations."""

    def list(self, email: str = "") -> List[Todo]:
        qs = Todo.objects.all()
        if email:
            qs = qs.filter(email=email)
        return list(qs.order_by("created_at"))

    def create(self, email: str, title: str, completed: bool = False) -> Todo:
        return Todo.objects.create(email=email, title=title, completed=completed)

    def get_by_id(self, todo_id: uuid.UUID) -> Optional[Todo]:
        try:
            return Todo.objects.get(pk=todo_id)
        except Todo.DoesNotExist:
            return None

    def update(
        self,
        todo: Todo,
        title: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> Todo:
        if title is not None:
            todo.title = title
        if completed is not None:
            todo.completed = completed
        todo.save()
        return todo

    def delete(self, todo: Todo) -> None:
        todo.delete()

    def clear(self, email: str = "") -> None:
        qs = Todo.objects.all()
        if email:
            qs = qs.filter(email=email)
        qs.delete()
