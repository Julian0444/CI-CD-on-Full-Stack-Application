from django.db import models


class User(models.Model):
    """
    Application user.

    Mirrors the Go model: email (unique, normalized) + password (plain text).
    This is NOT Django's auth User — it is a domain-specific model to
    preserve the exact behaviour of the original Go backend.
    """

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = "app_users"
        ordering = ["email"]

    def __str__(self):
        return self.email
