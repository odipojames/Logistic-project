from rest_framework import permissions
from companies.models import TransporterCompany, CargoOwnerCompany, Company
from rest_framework.permissions import SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    to allow only admit to delete update and post
    """

    message = "you must be shypper admin to perform this"

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return str(request.user.role) == "superuser"


class IsAllowedToOrder(permissions.BasePermission):
    """
    cargo owner permissions
    """

    message = "you must be a cargo Owner to permform this"

    def has_permission(self, request, view):
        return request.user.role == "carogo-owner-director"


class IsTransporterOrAdmin(permissions.BasePermission):
    """
    permissions for creating and getting drivers
    """

    message = "you must be a transporter or superuser to perform this"

    def has_permission(self, request, view):
        if str(request.user.role) == "staff" and request.method in SAFE_METHODS:
            return True
        return (
            str(request.user.role) == "transporter-director"
            or str(request.user.role) == "superuser"
            or str(request.user.role) == "admin"
        )


class IsAdminOrCargoOwner(permissions.BasePermission):
    """
    allow only cargo owners and admin to perform spacific actions
    """

    message = "you dont have an access to this action"

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return (
                str(request.user.role) == "cargo-owner-director"
                or str(request.user.role) == "superuser"
            )

    def has_object_permission(self, request, view, obj):
        """allow only owner or admin to delete and uptade depots"""
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsShyperAdmin(permissions.BasePermission):
    message = "you must be shyper admin to perform this"

    def has_permission(self, request, view):
        return request.user.is_authenticated and str(request.user.role) == "superuser"


class IsShyperEmployee(permissions.BasePermission):
    """allow only Shypper Employees or superuser"""

    message = "you must be shypper employee to perfom this"

    def has_permission(self, request, view):
        company = request.user.employer
        return (
            request.user.is_authenticated
            and request.user.is_superuser
            or request.user.is_authenticated
            and str(company.category) == "is_shypper"
        )


class IsAdminOrCompanyOwner(permissions.BasePermission):
    """
    check if shyper or cargo owner admin
    """

    message = "you must be a company owner who owns the obj to perform this"

    def has_permission(self, request, view):

        if request.method == "POST":
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        return obj.company.company_director == user or user.is_superuser


class IsAdminOrCargoOwnerRates(permissions.BasePermission):
    """
    allow only cargo owners and admin to perform spacific actions
    """

    message = "you dont have an access to this action"

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True
        else:
            return (
                str(request.user.role) == "cargo-owner-director"
                or str(request.user.role) == "superuser"
            )

    def has_object_permission(self, request, view, obj):
        """allow only owner or admin to delete and uptade depots"""
        if request.method in SAFE_METHODS:
            return True
        return (
            obj.created_by.company_director == request.user
            or str(request.user.role) == "superuser"
        )


class IsCargoOwner(permissions.BasePermission):
    """
    Allow only cargo owners
    """

    message = "You must be a cargo owner or admin"

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and str(request.user.role) == "cargo-owner-director"
        )

    def has_object_permission(self, request, view, obj):
        """allow only owner or admin to delete and update depots"""
        return obj.owner == request.user or str(request.user.role) == "superuser"


class IsAdminOrAssetOwner(permissions.BasePermission):
    """
    check if shyper or asset owner
    """

    message = "you must be an asset owner to perform this"

    def has_permission(self, request, view):

        if str(request.user.role) == "staff" and request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and (
            str(request.user.role) == "transporter-director"
            or str(request.user.role) == "superuser"
            or str(request.user.role) == "admin"
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if str(user.role) == "transporter-director":
            company = Company.objects.get(company_director=user)
            transporter = TransporterCompany.objects.get(company=company)

        if str(user.role) == "admin" or str(user.role) == "staff":
            company = user.employer
            transporter = TransporterCompany.objects.get(company=company)

        return obj.owned_by == transporter or user.is_superuser


class IsComponyAdminOrDirectorOrStaffReadOnly(permissions.BasePermission):
    """
    Directors and admins have full access. Staff users have read-only access.
    """

    message = "you must be admin or director to perfom this"

    def has_permission(self, request, view):
        user = request.user
        if str(user.role) == "staff" and request.method in SAFE_METHODS:
            return True
        return (
            str(user.role) == "transporter-director"
            or str(user.role) == "cargo-owner-director"
            or str(user.role) == "admin"
            or user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if (
            str(user.role) == "transporter-director"
            or str(user.role) == "cargo-owner-director"
        ):
            company = Company.objects.get(company_director=user)
        else:
            company = user.employer
        return obj.employer == company or user.is_superuser


class IsOwnerOrAdmin(permissions.BasePermission):
    """to allow only admin and owner of profile to edit profile"""

    message = "you must be the owner or admin to perform this action"

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS and request.user.is_authenticated:
            return True

        if (
            str(user.role) == "transporter-director"
            or str(user.role) == "cargo-owner-director"
        ):
            company = Company.objects.get(company_director=user)
            return obj.user.employer == company

        if str(user.role) == "admin":
            company = user.employer
            return obj.user.employer == company

        return obj.user == user or user.is_superuser


class IsCommodityOwner(permissions.BasePermission):
    """
    allow only cargo owners and admin to perform spacific actions
    """

    message = "you dont have an access to this action"

    def has_permission(self, request, view):
        if request.user.is_superuser == False:
            company = request.user.employer
            return (
                str(company.category) == "cargo_owner"
                or str(company.category) == "is_shypper"
            )
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        """allow only owners and their employess or admin to delete and uptade their commodity """
        if request.user.is_superuser == False:
            company = request.user.employer
            cargo_company = CargoOwnerCompany.objects.get(company=company)
            return obj.created_by == cargo_company
        return request.user.is_superuser
