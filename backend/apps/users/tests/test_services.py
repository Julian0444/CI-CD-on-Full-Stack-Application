"""Unit tests for UserService — business logic layer."""

import pytest

from apps.users.domain.exceptions import (
    InvalidCredentials,
    InvalidUserInput,
    UserAlreadyExists,
)
from apps.users.services.user_service import UserService


@pytest.mark.django_db
class TestUserServiceRegister:
    def setup_method(self):
        self.service = UserService()

    def test_register_stores_normalized_user(self):
        self.service.register(" User@Example.com ", " secret ")
        users = self.service.list_users()
        assert len(users) == 1
        assert users[0]["email"] == "user@example.com"

    def test_register_rejects_duplicates(self):
        self.service.register("user@example.com", "secret")
        with pytest.raises(UserAlreadyExists):
            self.service.register("user@example.com", "secret")

    def test_register_rejects_empty_email(self):
        with pytest.raises(InvalidUserInput):
            self.service.register("", "secret")

    def test_register_rejects_empty_password(self):
        with pytest.raises(InvalidUserInput):
            self.service.register("user@example.com", "")

    def test_register_rejects_whitespace_only(self):
        with pytest.raises(InvalidUserInput):
            self.service.register("   ", "   ")


@pytest.mark.django_db
class TestUserServiceLogin:
    def setup_method(self):
        self.service = UserService()

    def test_login_succeeds_with_valid_credentials(self):
        self.service.register("user@example.com", "secret")
        # Should not raise
        self.service.login(" User@Example.com ", " secret ")

    def test_login_fails_with_wrong_password(self):
        self.service.register("user@example.com", "secret")
        with pytest.raises(InvalidCredentials):
            self.service.login("user@example.com", "wrong")

    def test_login_fails_with_unknown_email(self):
        with pytest.raises(InvalidCredentials):
            self.service.login("unknown@example.com", "secret")

    def test_login_fails_with_empty_email(self):
        with pytest.raises(InvalidCredentials):
            self.service.login("", "secret")

    def test_login_fails_with_empty_password(self):
        with pytest.raises(InvalidCredentials):
            self.service.login("user@example.com", "")


@pytest.mark.django_db
class TestUserServiceListAndClear:
    def setup_method(self):
        self.service = UserService()

    def test_list_returns_public_users(self):
        self.service.register("alice@example.com", "alice")
        self.service.register("bob@example.com", "bob")
        users = self.service.list_users()
        assert len(users) == 2
        emails = [u["email"] for u in users]
        assert "alice@example.com" in emails
        assert "bob@example.com" in emails
        # Password must NOT be in the response
        for u in users:
            assert "password" not in u

    def test_clear_removes_all_users(self):
        self.service.register("alice@example.com", "alice")
        self.service.register("bob@example.com", "bob")
        self.service.clear()
        users = self.service.list_users()
        assert len(users) == 0
