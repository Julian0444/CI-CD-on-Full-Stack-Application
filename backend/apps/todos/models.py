import uuid

from django.db import models


class Todo(models.Model):
    """
    Task entity.

    Uses UUID as primary key to generate string IDs comparable to
    MongoDB ObjectIDs (the Go backend used 24-char hex ObjectIDs).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    title = models.CharField(max_length=500)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "app_todos"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.title} ({self.email})"
