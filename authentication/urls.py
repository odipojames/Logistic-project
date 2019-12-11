from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import RegistrationAPIView, LoginAPIView, UserUpdateAPIView, logout_view

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("user_update/", UserUpdateAPIView.as_view(), name="user_update"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("logout/", logout_view, name="logout"),
]
