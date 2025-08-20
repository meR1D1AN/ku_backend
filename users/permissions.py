from rest_framework.permissions import BasePermission

from all_fixture.choices import RoleChoices


class IsAdminUser(BasePermission):
    """
    Доступ только для суперпользователей (администраторов).
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_superuser


class IsOrdinaryUser(BasePermission):
    """
    Доступ только для обычных пользователей (RoleChoices.USER),
    причём пользователь может видеть только свои данные.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == RoleChoices.USER

    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ только к своим данным
        return obj == request.user


class IsCompanyUser(BasePermission):
    """
    Доступ для Туроператоров и Владельцев отелей.
    Они могут видеть только свои данные.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [RoleChoices.TOUR_OPERATOR, RoleChoices.HOTELIER]

    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ только к своим данным
        return obj == request.user


class IsAdminOrOwner(BasePermission):
    """
    Доступ для админов или владельца аккаунта.
    Только владелец может просматривать или редактировать свои данные.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Только админ или владелец аккаунта
        return request.user.is_superuser or obj == request.user
