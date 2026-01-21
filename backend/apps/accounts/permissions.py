from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.role == 'ADMIN' or request.user.is_staff)

class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'DRIVER'

class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'CLIENT'

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute, or `user`, or `client`/`driver`.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # IF we want to restrict read access too, remove this next line.
        # if request.method in permissions.SAFE_METHODS:
        #     return True

        if request.user.role == 'ADMIN' or request.user.is_staff:
            return True

        # Check various common owner field names
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'client'):
            return obj.client == request.user
        if hasattr(obj, 'driver'):
            # Driver might be a profile or user FK
            if hasattr(obj.driver, 'user'):
                return obj.driver.user == request.user
            return obj.driver == request.user
        
        if hasattr(obj, 'drivers'):
            # Many-to-Many field for drivers (like in Vehicle)
            # Check if current user is in the list of drivers
            return obj.drivers.filter(id=request.user.id).exists()

        if hasattr(obj, 'sender'):
             return obj.sender == request.user
            
        return False
