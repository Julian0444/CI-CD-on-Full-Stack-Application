from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ("title", "email", "completed", "created_at")
    list_filter = ("completed", "email")
    search_fields = ("title", "email")
