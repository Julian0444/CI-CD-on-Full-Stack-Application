"""Unit tests for TodoService — business logic layer."""

import pytest

from apps.todos.domain.exceptions import InvalidTodoID, InvalidTodoInput, TodoNotFound
from apps.todos.services.todo_service import TodoService


@pytest.mark.django_db
class TestTodoServiceCreate:
    def setup_method(self):
        self.service = TodoService()

    def test_create_normalizes_input(self):
        result = self.service.create(" User@Example.com ", " Primera tarea ")
        assert result["email"] == "user@example.com"
        assert result["title"] == "Primera tarea"
        assert result["completed"] is False
        assert result["id"]  # Non-empty string
        assert result["createdAt"]  # Non-empty timestamp

    def test_create_rejects_empty_email(self):
        with pytest.raises(InvalidTodoInput):
            self.service.create("", "Some title")

    def test_create_rejects_empty_title(self):
        with pytest.raises(InvalidTodoInput):
            self.service.create("user@example.com", "")

    def test_create_rejects_whitespace_only(self):
        with pytest.raises(InvalidTodoInput):
            self.service.create("   ", "   ")


@pytest.mark.django_db
class TestTodoServiceList:
    def setup_method(self):
        self.service = TodoService()

    def test_list_all(self):
        self.service.create("alice@example.com", "Task A")
        self.service.create("bob@example.com", "Task B")
        todos = self.service.list()
        assert len(todos) == 2

    def test_list_filters_by_email(self):
        self.service.create("alice@example.com", "Task A")
        self.service.create("bob@example.com", "Task B")
        todos = self.service.list("bob@example.com")
        assert len(todos) == 1
        assert todos[0]["email"] == "bob@example.com"

    def test_list_normalizes_email_filter(self):
        self.service.create("bob@example.com", "Task B")
        todos = self.service.list(" Bob@Example.com ")
        assert len(todos) == 1


@pytest.mark.django_db
class TestTodoServiceUpdate:
    def setup_method(self):
        self.service = TodoService()

    def test_update_title_and_completed(self):
        created = self.service.create("alice@example.com", "Initial")
        updated = self.service.update(
            created["id"], title="Updated", completed=True
        )
        assert updated["title"] == "Updated"
        assert updated["completed"] is True

    def test_update_only_completed(self):
        created = self.service.create("alice@example.com", "Initial")
        updated = self.service.update(created["id"], completed=True)
        assert updated["completed"] is True
        assert updated["title"] == "Initial"

    def test_update_rejects_empty_update(self):
        created = self.service.create("alice@example.com", "Initial")
        with pytest.raises(InvalidTodoInput):
            self.service.update(created["id"])

    def test_update_rejects_invalid_id(self):
        with pytest.raises(InvalidTodoID):
            self.service.update("invalid-id", title="x")

    def test_update_rejects_not_found(self):
        with pytest.raises(TodoNotFound):
            self.service.update(
                "00000000-0000-0000-0000-000000000000", title="x"
            )

    def test_update_rejects_empty_title_after_trim(self):
        created = self.service.create("alice@example.com", "Initial")
        with pytest.raises(InvalidTodoInput):
            self.service.update(created["id"], title="   ")


@pytest.mark.django_db
class TestTodoServiceDelete:
    def setup_method(self):
        self.service = TodoService()

    def test_delete_removes_todo(self):
        created = self.service.create("alice@example.com", "To Delete")
        self.service.delete(created["id"])
        todos = self.service.list("alice@example.com")
        assert len(todos) == 0

    def test_delete_rejects_invalid_id(self):
        with pytest.raises(InvalidTodoID):
            self.service.delete("invalid-id")

    def test_delete_rejects_not_found(self):
        with pytest.raises(TodoNotFound):
            self.service.delete("00000000-0000-0000-0000-000000000000")


@pytest.mark.django_db
class TestTodoServiceClear:
    def setup_method(self):
        self.service = TodoService()

    def test_clear_by_email(self):
        self.service.create("alice@example.com", "Task A")
        self.service.create("bob@example.com", "Task B")
        self.service.clear("alice@example.com")
        assert len(self.service.list("alice@example.com")) == 0
        assert len(self.service.list("bob@example.com")) == 1

    def test_clear_all(self):
        self.service.create("alice@example.com", "Task A")
        self.service.create("bob@example.com", "Task B")
        self.service.clear()
        assert len(self.service.list()) == 0
