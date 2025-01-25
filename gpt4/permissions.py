from rest_framework.permissions import BasePermission, SAFE_METHODS


# SAFE_METHODS: GET, HEAD или OPTIONS
from gpt4.utils import cons


class IsOwnerOrStaffOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            # пров. что юзер отправивший запрос и owner в модели один и тот же юзер или юзер отностися к персоналу прил.
            request.user.is_authenticated and (obj.owner == request.user or request.user.is_staff)
        )

class CreateOnlyAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        return True

class IsOwnerOrStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True

        # проверяем, пытается ли пользователь получить книги своего аккаунта
        owner_id = view.kwargs.get('pk')
        if owner_id is None or not owner_id.isdigit():
            cons(owner_id)
            return False

        return int(owner_id) == request.user.id