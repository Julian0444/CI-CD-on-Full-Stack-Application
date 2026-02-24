"""API-level tests for todo endpoints — verifies HTTP contract."""

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestCreateTodoEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_create_success(self):
        response = self.client.post(
            "/todos",
            {"email": "tasks@example.com", "title": "Primera tarea"},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["todo"]["title"] == "Primera tarea"
        assert data["todo"]["completed"] is False
        assert "id" in data["todo"]
        assert "createdAt" in data["todo"]

    def test_create_rejects_empty_fields(self):
        response = self.client.post(
            "/todos",
            {"email": "", "title": ""},
            format="json",
        )
        assert response.status_code == 400
        assert response.json() == {"error": "email y titulo son requeridos"}


@pytest.mark.django_db
class TestListTodosEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_list_empty(self):
        response = self.client.get("/todos")
        assert response.status_code == 200
        assert response.json() == {"todos": []}

    def test_list_filtered_by_email(self):
        self.client.post(
            "/todos",
            {"email": "tasks@example.com", "title": "Task 1"},
            format="json",
        )
        self.client.post(
            "/todos",
            {"email": "other@example.com", "title": "Task 2"},
            format="json",
        )
        response = self.client.get("/todos?email=tasks@example.com")
        assert response.status_code == 200
        data = response.json()
        assert len(data["todos"]) == 1
        assert data["todos"][0]["email"] == "tasks@example.com"


@pytest.mark.django_db
class TestUpdateTodoEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_update_success(self):
        create_resp = self.client.post(
            "/todos",
            {"email": "tasks@example.com", "title": "Original"},
            format="json",
        )
        todo_id = create_resp.json()["todo"]["id"]

        response = self.client.put(
            f"/todos/{todo_id}",
            {"title": "Actualizada", "completed": True},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["todo"]["title"] == "Actualizada"
        assert data["todo"]["completed"] is True

    def test_update_invalid_id(self):
        response = self.client.put(
            "/todos/invalid-id",
            {"completed": True},
            format="json",
        )
        assert response.status_code == 400
        assert response.json() == {"error": "id invalido"}

    def test_update_not_found(self):
        response = self.client.put(
            "/todos/00000000-0000-0000-0000-000000000000",
            {"title": "x"},
            format="json",
        )
        assert response.status_code == 404
        assert response.json() == {"error": "tarea no encontrada"}

    def test_update_nothing_to_update(self):
        create_resp = self.client.post(
            "/todos",
            {"email": "tasks@example.com", "title": "Original"},
            format="json",
        )
        todo_id = create_resp.json()["todo"]["id"]
        response = self.client.put(
            f"/todos/{todo_id}",
            {},
            format="json",
        )
        assert response.status_code == 400
        assert response.json() == {"error": "nada para actualizar"}


@pytest.mark.django_db
class TestDeleteTodoEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_delete_success(self):
        create_resp = self.client.post(
            "/todos",
            {"email": "tasks@example.com", "title": "To Delete"},
            format="json",
        )
        todo_id = create_resp.json()["todo"]["id"]

        response = self.client.delete(f"/todos/{todo_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "tarea eliminada"}

        # Verify it's gone
        list_resp = self.client.get("/todos?email=tasks@example.com")
        assert len(list_resp.json()["todos"]) == 0

    def test_delete_invalid_id(self):
        response = self.client.delete("/todos/invalid-id")
        assert response.status_code == 400
        assert response.json() == {"error": "id invalido"}

    def test_delete_not_found(self):
        response = self.client.delete(
            "/todos/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404
        assert response.json() == {"error": "tarea no encontrada"}


@pytest.mark.django_db
class TestClearTodosEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_clear_by_email(self):
        self.client.post(
            "/todos",
            {"email": "tasks@example.com", "title": "Task 1"},
            format="json",
        )
        response = self.client.delete("/todos?email=tasks@example.com")
        assert response.status_code == 200
        assert response.json() == {"message": "tareas eliminadas"}

    def test_clear_all(self):
        self.client.post(
            "/todos",
            {"email": "tasks@example.com", "title": "Task 1"},
            format="json",
        )
        response = self.client.delete("/todos")
        assert response.status_code == 200
        assert response.json() == {"message": "tareas eliminadas"}


@pytest.mark.django_db
class TestFullTodoCRUDFlow:
    """Integration-style test that mirrors the Go test_handler flow."""

    def setup_method(self):
        self.client = APIClient()

    def test_create_list_update_delete_flow(self):
        # Register user (for completeness)
        self.client.post(
            "/register",
            {"email": "tasks@example.com", "password": "secret"},
            format="json",
        )

        # Create todo
        create_resp = self.client.post(
            "/todos",
            {"email": "tasks@example.com", "title": "Primera tarea"},
            format="json",
        )
        assert create_resp.status_code == 201
        todo = create_resp.json()["todo"]
        assert todo["title"] == "Primera tarea"
        assert todo["completed"] is False
        todo_id = todo["id"]

        # List todos filtered by email
        list_resp = self.client.get("/todos?email=tasks@example.com")
        assert list_resp.status_code == 200
        assert len(list_resp.json()["todos"]) == 1
        assert list_resp.json()["todos"][0]["id"] == todo_id

        # Update todo
        update_resp = self.client.put(
            f"/todos/{todo_id}",
            {"title": "Actualizada", "completed": True},
            format="json",
        )
        assert update_resp.status_code == 200
        updated = update_resp.json()["todo"]
        assert updated["title"] == "Actualizada"
        assert updated["completed"] is True

        # Delete todo
        delete_resp = self.client.delete(f"/todos/{todo_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json() == {"message": "tarea eliminada"}

        # Verify list is empty
        list_resp2 = self.client.get("/todos?email=tasks@example.com")
        assert list_resp2.status_code == 200
        assert len(list_resp2.json()["todos"]) == 0
