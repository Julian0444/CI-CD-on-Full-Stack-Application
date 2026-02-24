"""
Root URL configuration.

Routes are kept at the root level (no /api/ prefix) to preserve
the exact API contract from the Go backend.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Django admin (optional, not part of API contract)
    path("admin/", admin.site.urls),
    # API documentation (additive, does not break existing contract)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # App routes — mounted at root to match Go paths
    path("", include("apps.health.api.urls")),
    path("", include("apps.users.api.urls")),
    path("", include("apps.todos.api.urls")),
]
