from rest_framework.permissions import BasePermission


class IsBranchAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.position == 'admin' or request.user.position == 'super_admin'


class IsOperator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.position == 'operator'


class IsRegistrator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.position == 'registrator'


class IsOperatorOrRegistrator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.position == 'registrator' or request.user.position == 'operator'


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user == obj.client