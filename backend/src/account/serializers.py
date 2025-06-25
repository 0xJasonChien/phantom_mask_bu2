from typing import ClassVar, Self

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User
from .validators import CaptchaValidator


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
    hashkey = serializers.CharField()


class UserLoginSerializer(TokenObtainPairSerializer):
    captcha = serializers.CharField()
    captcha_hash_key = serializers.CharField()

    def __init__(
        self: Self,
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.validators.append(CaptchaValidator())
