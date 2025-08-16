from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    """
    Custom permission class that only allows unauthenticated users.
    This is useful for views like password reset that should only be accessible
    to users who are not logged in.
    """
    
    def has_permission(self, request, view):
        # Return True if user is NOT authenticated
        return not request.user.is_authenticated
    
    def message(self):
        return "This endpoint is only accessible to unauthenticated users."