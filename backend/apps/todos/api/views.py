"""
HTTP views for todo operations.

Views are thin — business logic lives in TodoService.
Error messages match the Go backend exactly to preserve the API contract.
"""

import logging
from typing import Optional

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.todos.domain.exceptions import InvalidTodoID, InvalidTodoInput, TodoNotFound
from apps.todos.services.todo_service import TodoService

logger = logging.getLogger(__name__)

_service: Optional[TodoService] = None


def _get_service() -> TodoService:
    global _service
    if _service is None:
        _service = TodoService()
    return _service


def reset_service(service: Optional[TodoService] = None) -> None:
    """Replace the module-level service (useful for testing)."""
    global _service
    _service = service


@api_view(["GET", "POST", "DELETE"])
def todos_collection(request):
    """
    GET    /todos?email=...  -> list todos
    POST   /todos            -> create todo
    DELETE /todos?email=...  -> clear todos
    """
    service = _get_service()

    if request.method == "GET":
        return _list_todos(request, service)
    elif request.method == "POST":
        return _create_todo(request, service)
    else:  # DELETE
        return _clear_todos(request, service)


@api_view(["PUT", "DELETE"])
def todos_detail(request, todo_id):
    """
    PUT    /todos/:id -> update todo
    DELETE /todos/:id -> delete todo
    """
    service = _get_service()

    if request.method == "PUT":
        return _update_todo(request, service, todo_id)
    else:  # DELETE
        return _delete_todo(request, service, todo_id)


# -- Private helpers ──────────────────────────────────────────


def _list_todos(request, service):
    email = request.query_params.get("email", "")
    try:
        todos = service.list(email)
        return Response({"todos": todos}, status=status.HTTP_200_OK)
    except Exception:
        logger.exception("Error al obtener tareas")
        return Response(
            {"error": "error al obtener tareas"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _create_todo(request, service):
    if not isinstance(request.data, dict):
        return Response(
            {"error": "datos invalidos"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = request.data.get("email", "")
    title = request.data.get("title", "")

    try:
        todo = service.create(email, title)
        return Response({"todo": todo}, status=status.HTTP_201_CREATED)
    except InvalidTodoInput:
        return Response(
            {"error": "email y titulo son requeridos"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        logger.exception("Error al crear tarea")
        return Response(
            {"error": "error al crear tarea"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _clear_todos(request, service):
    email = request.query_params.get("email", "")
    try:
        service.clear(email)
        return Response(
            {"message": "tareas eliminadas"},
            status=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Error al limpiar tareas")
        return Response(
            {"error": "error al limpiar tareas"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _update_todo(request, service, todo_id):
    if not isinstance(request.data, dict):
        return Response(
            {"error": "datos invalidos"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    title = request.data.get("title")
    completed = request.data.get("completed")

    try:
        todo = service.update(todo_id, title=title, completed=completed)
        return Response({"todo": todo}, status=status.HTTP_200_OK)
    except InvalidTodoInput:
        return Response(
            {"error": "nada para actualizar"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except InvalidTodoID:
        return Response(
            {"error": "id invalido"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except TodoNotFound:
        return Response(
            {"error": "tarea no encontrada"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception:
        logger.exception("Error al actualizar tarea")
        return Response(
            {"error": "error al actualizar tarea"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _delete_todo(request, service, todo_id):
    try:
        service.delete(todo_id)
        return Response(
            {"message": "tarea eliminada"},
            status=status.HTTP_200_OK,
        )
    except InvalidTodoID:
        return Response(
            {"error": "id invalido"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except TodoNotFound:
        return Response(
            {"error": "tarea no encontrada"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception:
        logger.exception("Error al eliminar tarea")
        return Response(
            {"error": "error al eliminar tarea"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
