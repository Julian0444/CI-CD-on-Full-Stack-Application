"""API-level tests for user endpoints — verifies HTTP contract."""

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestRegisterEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_register_success(self):
        response = self.client.post(
            "/register",
            {"email": "User@example.com", "password": "secret"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json() == {"message": "usuario registrado con exito"}

    def test_register_rejects_duplicate(self):
        self.client.post(
            "/register",
            {"email": "duplicate@example.com", "password": "secret"},
            format="json",
        )
        response = self.client.post(
            "/register",
            {"email": "duplicate@example.com", "password": "secret"},
            format="json",
        )
        assert response.status_code == 409
        assert response.json() == {"error": "usuario ya existe"}

    def test_register_rejects_empty_fields(self):
        response = self.client.post(
            "/register",
            {"email": "", "password": ""},
            format="json",
        )
        assert response.status_code == 400
        assert response.json() == {"error": "email y clave son requeridos"}

    def test_register_missing_fields_returns_validation_error(self):
        response = self.client.post(
            "/register",
            {"email": "user@test.com", "password": "   "},
            format="json",
        )
        assert response.status_code == 400
        assert response.json() == {"error": "email y clave son requeridos"}


@pytest.mark.django_db
class TestLoginEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_login_success(self):
        self.client.post(
            "/register",
            {"email": "user@example.com", "password": "secret"},
            format="json",
        )
        response = self.client.post(
            "/login",
            {"email": "user@example.com", "password": "secret"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json() == {"message": "login exitoso"}

    def test_login_invalid_credentials(self):
        response = self.client.post(
            "/login",
            {"email": "unknown@example.com", "password": "secret"},
            format="json",
        )
        assert response.status_code == 401
        assert response.json() == {"error": "credenciales invalidas"}

    def test_login_normalizes_email(self):
        self.client.post(
            "/register",
            {"email": "User@Example.com", "password": "secret"},
            format="json",
        )
        response = self.client.post(
            "/login",
            {"email": "user@example.com", "password": "secret"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["message"] == "login exitoso"


@pytest.mark.django_db
class TestUsersEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_list_users(self):
        self.client.post(
            "/register",
            {"email": "User@example.com", "password": "secret"},
            format="json",
        )
        response = self.client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 1
        assert data["users"][0]["email"] == "user@example.com"
        assert "password" not in data["users"][0]

    def test_clear_users(self):
        self.client.post(
            "/register",
            {"email": "user@example.com", "password": "secret"},
            format="json",
        )
        response = self.client.delete("/users")
        assert response.status_code == 200
        assert response.json() == {"message": "usuarios eliminados"}

        # Verify list is empty
        list_response = self.client.get("/users")
        assert list_response.json()["users"] == []
