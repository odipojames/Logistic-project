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
