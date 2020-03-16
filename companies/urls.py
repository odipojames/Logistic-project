from django.urls import path
from companies.views import (
    CargoOwnerCompanyListAPIView,
    CreatePersonOfContact,
    PersonOfContactRetrieveUpdateDestroyAPIView,
    CargoOwnerCompanyRetrieveUpdateDestroy,
    TransporterCompanyListAPIView,
    TransporterCompanyRetrieveUpdateDestroy,
    EmployeeListCreateAPIView,
    EmployeeRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path(
        "cargo-owner/", CargoOwnerCompanyListAPIView.as_view(), name="cargo-companies"
    ),
    path(
        "cargo-owner/<int:pk>/",
        CargoOwnerCompanyRetrieveUpdateDestroy.as_view(),
        name="cargo-owner-company",
    ),
    path(
        "transporter/",
        TransporterCompanyListAPIView.as_view(),
        name="transporter-companies",
    ),
    path(
        "transporter/<int:pk>/",
        TransporterCompanyRetrieveUpdateDestroy.as_view(),
        name="transporter-company",
    ),
    path(
        "person-of-contact/",
        CreatePersonOfContact.as_view(),
        name="register-person-of-contact",
    ),
    path(
        "person-of-contact/<int:pk>/",
        PersonOfContactRetrieveUpdateDestroyAPIView.as_view(),
        name="update-person-of-contact",
    ),
    path("employees/", EmployeeListCreateAPIView.as_view(), name="create-employee"),
    path(
        "employee/<int:pk>",
        EmployeeRetrieveUpdateDestroyAPIView.as_view(),
        name="detail-employee",
    ),
]
