from rest_framework import permissions


class IsFarmer(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role.is_farmer


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role.is_admin
