from typing import Self

from captcha.models import CaptchaStore
from captcha.views import captcha_image
from django.http import HttpRequest, HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    CaptchaRetrieveSerializer,
    TokenRetrieveSerializer,
    UserCreateSerializer,
    UserLoginSerializer,
)


class UserCreateView(CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = ()
    queryset = User.objects.all()

    @extend_schema(
        operation_id='建立使用者帳號',
        responses={
            HTTP_201_CREATED: TokenRetrieveSerializer,
        },
    )
    def post(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        return super().post(request, *args, **kwargs)

    def create(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> Response:
        # validate data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create user
        validated_data = serializer.validated_data
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # generate tokens
        refresh = RefreshToken.for_user(user)

        # create response with token data
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(response_data, status=HTTP_201_CREATED)


class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    @extend_schema(
        operation_id='使用者登入',
        responses={
            HTTP_200_OK: TokenRetrieveSerializer,
        },
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

    @extend_schema(
        operation_id='取得驗證碼',
        responses={
            HTTP_200_OK: CaptchaRetrieveSerializer,
        },
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


class CaptchaImageRetrieveView(RetrieveAPIView):
    permission_classes = ()

    @extend_schema(
        operation_id='取得驗證碼圖形',
    )
    def get(
        self: Self,
        request: HttpRequest,
        *args: tuple,
        **kwargs: dict,
    ) -> HttpResponse:
        hash_key = self.kwargs['hash_key']
        return captcha_image(request, hash_key, scale=2)
