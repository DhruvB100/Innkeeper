from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Only allow the author of an object to edit or delete it.
    Anyone can read.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the author
        return obj.author == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Only admins can write, everyone can read"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'


class IsApprovedUser(permissions.BasePermission):
    """
    Only allow approved users to perform actions.
    Unapproved users can't post or comment.
    """

    message = 'Your account is pending approval. Please wait for an admin to approve your account.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_approved
