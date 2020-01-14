from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    '''
    shipper permissions
    '''
    message = 'you must be a shipper to permform this'
    def has_permission(self, request, view):
        return request.user.role=='SA'


class IsAllowedToOrder(permissions.BasePermission):
    '''
    cargo owner permissions
    '''
    message = 'you must be a cargo Owner to permform this'
    def has_permission(self, request, view):
        return request.user.role == "CO"

class IsTransporterOrAdmin(permissions.BasePermission):
    '''
    permissions for creating and getting drivers
    '''
    message = 'you must be a transporter or superuser to perform this'
    
    def has_permission(self, request, view):
        return str(request.user.role) == "transporter" or str(request.user.role) == "superuser"