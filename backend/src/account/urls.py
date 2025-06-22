from captcha.views import captcha_image
from django.urls import path, re_path

from .views import CaptchaHashKeyRetrieveView, UserCreateView, UserLoginView

urlpatterns = [
    path('register/', UserCreateView.as_view()),
    path('login/', UserLoginView.as_view()),
    re_path(r'captcha/image/(?P<key>\w+)/$', captcha_image, kwargs={'scale': 2}),
    path('captcha/', CaptchaHashKeyRetrieveView.as_view()),
]
