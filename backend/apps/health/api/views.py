from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def healthz(request):
    """Health-check endpoint. Returns {"status": "ok"}."""
    return Response({"status": "ok"}, status=status.HTTP_200_OK)
