from rest_framework import permissions


class IsStylist(permissions.BasePermission):
    """Allows access only to users with a linked StylistProfile."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, "stylist_profile"))
