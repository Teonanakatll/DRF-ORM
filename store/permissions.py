from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrStaffOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            # проверяем что хозяин обьекта и юзер отправивший запрос это один и тот же юзер
            request.user.is_authenticated and (obj.owner == request.user or request.user.is_staff)
        )
