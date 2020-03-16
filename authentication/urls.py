from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import (
    RegistrationAPIView,
    LoginAPIView,
    UserUpdateAPIView,
    logout_view,
    ProfileRetrieveUpdateDestroyAPIView,
    ListProfileAPIView,
)

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("user_update/", UserUpdateAPIView.as_view(), name="user_update"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("logout/", logout_view, name="logout"),
    path(
        "reset-password/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("user_profile/", ListProfileAPIView.as_view(), name="profiles"),
    path(
        "user_profile/<int:pk>",
        ProfileRetrieveUpdateDestroyAPIView.as_view(),
        name="ususer_profile",
    ),
]
