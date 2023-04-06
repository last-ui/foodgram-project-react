from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Кастомный перминш ограничивающий права не автора рецептов."""
    message = 'Доступ только для автора!'

    def has_object_permission(self, request, view, obj):
        """Пользователь не может редактировать чужой пост."""
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )
