from rest_framework import permissions
from companies.models import TransporterCompany
from rest_framework.permissions import SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    to allow only admit to delete update and post
    """
    message = 'you must be shypper admin to perform this'
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return str(request.user.role) == 'superuser'


class IsAllowedToOrder(permissions.BasePermission):
    '''
    cargo owner permissions
    '''
    message = 'you must be a cargo Owner to permform this'
    def has_permission(self, request, view):
        return request.user.role == "carogo-owner"

class IsTransporterOrAdmin(permissions.BasePermission):
    '''
    permissions for creating and getting drivers
    '''
    message = 'you must be a transporter or superuser to perform this'

    def has_permission(self, request, view):
        return str(request.user.role) == "transporter" or str(request.user.role) == "superuser"


class IsAdminOrCargoOwner(permissions.BasePermission):
    """
    check if shyper or cargo owner admin
    """
    message = 'you must be a cargo owner or superuser to perform this'

    def has_permission(self, request, view):

        return str(request.user.role) == "cargo-owner" or str(request.user.role) == "superuser"
