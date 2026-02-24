import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestHealthEndpoint:
    def setup_method(self):
        self.client = APIClient()

    def test_healthz_returns_ok(self):
        response = self.client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
