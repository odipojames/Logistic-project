from django.urls import path
from .views import  *

urlpatterns = [
    path('register/transporter/',TransporterRegistrationAPIView.as_view(),name='transporter'),
    path('register/cargo-owner/',CargoOwnerRegistrationAPIView.as_view(),name='cargo-owner'),
]
