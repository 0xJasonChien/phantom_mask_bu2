from django.urls import path, re_path

from .views import (
    CaptchaHashKeyRetrieveView,
    CaptchaImageRetrieveView,
    UserCreateView,
    UserLoginView,
)

urlpatterns = [
    path('register/', UserCreateView.as_view()),
    path('login/', UserLoginView.as_view()),
    re_path(r'captcha/image/(?P<hash_key>\w+)/$', CaptchaImageRetrieveView.as_view()),
    path('captcha/', CaptchaHashKeyRetrieveView.as_view()),
]
