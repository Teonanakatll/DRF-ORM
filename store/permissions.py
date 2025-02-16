from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrStaffOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            # проверяем что хозяин обьекта и юзер отправивший запрос это один и тот же юзер
            request.user.is_authenticated and (obj.owner == request.user or request.user.is_staff)
        )

# class IsStaffOrSuperuserOrReadOnly(BasePermission):
#     def has_permission(self, request, view):
#         if request.method == 'POST':  # Только для POST-запросов
#             return request.user and request.user.is_staff
#         elif request.method == 'DELETE':  # Только для DELETE-запросов
#             return request.user and request.user.is_superuser
#         return True  # Для всех остальных методов доступ открыт
