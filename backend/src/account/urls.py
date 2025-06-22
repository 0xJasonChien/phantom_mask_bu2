from django.urls import include, path

from .views import CapChaRetrieveView, UserCreateView, UserLoginView

urlpatterns = [
    path('register/', UserCreateView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('captcha/', include('captcha.urls')),
    path('get-captcha-key/', CapChaRetrieveView.as_view()),
]
