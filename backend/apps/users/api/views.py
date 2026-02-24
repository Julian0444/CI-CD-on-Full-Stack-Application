"""
HTTP views for user operations.

Views are thin — business logic lives in UserService.
Error messages match the Go backend exactly to preserve the API contract.
"""

import logging
from typing import Optional

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.users.domain.exceptions import (
    InvalidCredentials,
    InvalidUserInput,
    UserAlreadyExists,
)
from apps.users.services.user_service import UserService

logger = logging.getLogger(__name__)

_service: Optional[UserService] = None


def _get_service() -> UserService:
    global _service
    if _service is None:
        _service = UserService()
    return _service


def reset_service(service: Optional[UserService] = None) -> None:
    """Replace the module-level service (useful for testing)."""
    global _service
    _service = service


@api_view(["POST"])
def register(request):
    """Handle user registration."""
    service = _get_service()

    email = request.data.get("email", "")
    password = request.data.get("password", "")

    if not isinstance(request.data, dict):
        return Response(
            {"error": "datos invalidos"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        service.register(email, password)
        return Response(
            {"message": "usuario registrado con exito"},
            status=status.HTTP_201_CREATED,
        )
    except InvalidUserInput:
        return Response(
            {"error": "email y clave son requeridos"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except UserAlreadyExists:
        return Response(
            {"error": "usuario ya existe"},
            status=status.HTTP_409_CONFLICT,
        )
    except Exception:
        logger.exception("Error al registrar usuario")
        return Response(
            {"error": "error al registrar usuario"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def login(request):
    """Handle user login."""
    service = _get_service()

    email = request.data.get("email", "")
    password = request.data.get("password", "")

    if not isinstance(request.data, dict):
        return Response(
            {"error": "datos invalidos"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        service.login(email, password)
        return Response(
            {"message": "login exitoso"},
            status=status.HTTP_200_OK,
        )
    except InvalidCredentials:
        return Response(
            {"error": "credenciales invalidas"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except Exception:
        logger.exception("Error al autenticar")
        return Response(
            {"error": "error al autenticar"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET", "DELETE"])
def users_view(request):
    """
    GET  /users → list all users (public representation).
    DELETE /users → remove all users (testing utility).
    """
    service = _get_service()

    if request.method == "GET":
        try:
            users = service.list_users()
            return Response({"users": users}, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("Error al obtener usuarios")
            return Response(
                {"error": "error al obtener usuarios"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # DELETE
    try:
        service.clear()
        return Response(
            {"message": "usuarios eliminados"},
            status=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error al limpiar usuarios")
        return Response(
            {"error": "error al limpiar usuarios"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
