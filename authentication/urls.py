from django.urls import path

from authentication.views import RegistrationAPIView, LoginAPIView, UserUpdateAPIView

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("user_update/", UserUpdateAPIView.as_view(), name="user_update"),
]
