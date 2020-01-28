from django.urls import path
from companies.views import (TransporterRegistrationAPIView, CargoOwnerRegistrationAPIView,
                                CreatePersonOfContact, PersonOfContactRetrieveUpdateDestroyAPIView)

urlpatterns = [
    path('register/transporter/',TransporterRegistrationAPIView.as_view(),name='transporter'),
    path('register/cargo-owner/',CargoOwnerRegistrationAPIView.as_view(),name='cargo-owner'),
    path('person-of-contact/', CreatePersonOfContact.as_view(), name='register-person-of-contact'),
    path('person-of-contact/<int:pk>/', PersonOfContactRetrieveUpdateDestroyAPIView.as_view(), name='update-person-of-contact'),
]
