from rest_framework import serializers


class CreateTodoSerializer(serializers.Serializer):
    email = serializers.CharField(required=False, default="", allow_blank=True)
    title = serializers.CharField(required=False, default="", allow_blank=True)


class UpdateTodoSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    completed = serializers.BooleanField(required=False, allow_null=True)
