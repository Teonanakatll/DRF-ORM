from rest_framework.permissions import BasePermission, SAFE_METHODS


# SAFE_METHODS: GET, HEAD или OPTIONS
class IsOwnerOrStuffOrReadOnly(BasePermission):
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
