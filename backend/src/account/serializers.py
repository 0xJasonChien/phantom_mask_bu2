from typing import ClassVar

from rest_framework import serializers

from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')
        extra_kwargs: ClassVar = {
            'password': {'write_only': True},
        }


class TokenRetrieveSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class CaptchaRetrieveSerializer(serializers.Serializer):
    hash_key = serializers.CharField()
