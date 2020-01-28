from django.urls import path
from companies.views import (TransporterRegistrationAPIView, CargoOwnerRegistrationAPIView,
                             CreatePersonOfContact, PersonOfContactRetrieveUpdateDestroyAPIView, CargoOwnerCompanyListAPIView, CargoOwnerCompanyRetrieveUpdateDestroy, TransporterCompanyListAPIView, TransporterCompanyRetrieveUpdateDestroy)

urlpatterns = [
    path('register/transporter/',
         TransporterRegistrationAPIView.as_view(), name='transporter'),
    path('register/cargo-owner/',
         CargoOwnerRegistrationAPIView.as_view(), name='cargo-owner'),
    path('cargo-owner/',
         CargoOwnerCompanyListAPIView.as_view(),
         name='cargo-owner-companies'),
    path('cargo-owner/<int:pk>/',
         CargoOwnerCompanyRetrieveUpdateDestroy.as_view(),
         name='cargo-owner-company'),
    path('transporter/',
         TransporterCompanyListAPIView.as_view(),
         name='transporter-companies'),
    path('transporter/<int:pk>/',
         TransporterCompanyRetrieveUpdateDestroy.as_view(),
         name='transporter-company'),
    path('person-of-contact/', CreatePersonOfContact.as_view(),
         name='register-person-of-contact'),
    path('person-of-contact/<int:pk>/',
         PersonOfContactRetrieveUpdateDestroyAPIView.as_view(), name='update-person-of-contact'),
]
