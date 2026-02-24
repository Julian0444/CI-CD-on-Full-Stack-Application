from django.urls import path

from . import views

urlpatterns = [
    path("todos", views.todos_collection, name="todos-collection"),
    path("todos/<str:todo_id>", views.todos_detail, name="todos-detail"),
]
