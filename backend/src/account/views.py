from typing import Self

from captcha.models import CaptchaStore
from django.http import HttpRequest, HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from account.apps import AccountConfig

from .models import User
from .serializers import (
    CaptchaRetrieveSerializer,
    TokenRetrieveSerializer,
    UserCreateSerializer,
)


class UserCreateView(CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(
        operation_id='建立使用者帳號',
        responses={
            HTTP_201_CREATED: TokenRetrieveSerializer,
        },
        tags=(AccountConfig.name,),
    )
    def post(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def perform_create(
        self: Self,
        serializer: UserCreateSerializer,
    ) -> User:
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        self.token_response = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return user

    def create(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        response = super().create(request, *args, **kwargs)
        response.data = self.token_response or {}
        return response


class UserLoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    @swagger_auto_schema(
        operation_id='使用者登入',
        responses={
            HTTP_200_OK: TokenRetrieveSerializer,
        },
        tags=(AccountConfig.name,),
    )
    def post(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().post(request, *args, **kwargs)


class CaptchaHashKeyRetrieveView(RetrieveAPIView):
    permission_classes = ()
    serializer_class = CaptchaRetrieveSerializer

    @swagger_auto_schema(
        operation_id='取得驗證碼',
        responses={
            HTTP_200_OK: CaptchaRetrieveSerializer,
        },
        tags=(AccountConfig.name,),
    )
    def get(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        hash_key = CaptchaStore.generate_key()
        serializer = self.serializer_class(data={'hash_key': hash_key})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=HTTP_200_OK)
