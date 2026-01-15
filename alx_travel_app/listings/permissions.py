from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a listing to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the listing
        return obj.owner == request.user


class IsGuestOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the guest who made a booking to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the guest who made the booking
        return obj.guest == request.user


class IsReviewOwner(permissions.BasePermission):
    """
    Custom permission to only allow the reviewer to edit or delete their review.
    """

    def has_object_permission(self, request, view, obj):
        # Only the guest who wrote the review can edit or delete it
        return obj.guest == request.user
