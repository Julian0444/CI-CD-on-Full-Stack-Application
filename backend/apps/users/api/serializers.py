from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    email = serializers.CharField(required=False, default="", allow_blank=True)
    password = serializers.CharField(required=False, default="", allow_blank=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=False, default="", allow_blank=True)
    password = serializers.CharField(required=False, default="", allow_blank=True)
