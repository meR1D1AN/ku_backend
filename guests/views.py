import logging

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated

from all_fixture.errors.list_error import (
    GUEST_ERROR,
    GUEST_PERMISSION_ERROR,
    GUEST_USER_ERROR,
)
from all_fixture.errors.serializers_error import (
    GuestErrorAuthSerializer,
    GuestErrorBaseSerializer,
    GuestErrorUserSerializer,
)
from all_fixture.views_fixture import GUEST_ID, GUEST_SETTINGS, ID_USER
from guests.models import Guest
from guests.serializers import GuestDetailSerializer, GuestSerializer
from users.models import User

logger = logging.getLogger(__name__)


class UserRelatedViewSet(viewsets.ModelViewSet):
    user_lookup_field = "user_id"
    error_message = None

    def get_user(self):
        if not hasattr(self, "_user_id"):
            user_id = self.kwargs.get(self.user_lookup_field)
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise NotFound({"detail": GUEST_USER_ERROR}) from None
        return self._user_id

    def check_permissions_for_user(self, user):
        """Проверяет, может ли текущий пользователь работать с указанным user_id."""
        if user is None or self.request.user.is_superuser:
            return
        if user.id != self.request.user.id:
            logger.warning(f"Пользователь {self.request.user.id} пытался получить доступ к данным user_id={user.id}")
            raise PermissionDenied({"detail": GUEST_PERMISSION_ERROR}) from None


@extend_schema(tags=[GUEST_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список гостей",
        description="Получение списка всех гостей. Доступен только авторизованным пользователям.",
        parameters=[ID_USER],
        responses={
            200: OpenApiResponse(
                response=GuestSerializer(many=True),
                description="Успешное получение всех гостей",
            ),
            401: OpenApiResponse(
                response=GuestErrorAuthSerializer,
                description="Ошибка: Пользователь не авторизирован",
            ),
            404: OpenApiResponse(
                response=GuestErrorUserSerializer,
                description="Ошибка: Турист не найден",
            ),
        },
    ),
    create=extend_schema(
        summary="Добавление Гостя",
        description="Создание нового Гостя. Доступно только авторизованным пользователям.",
        request=GuestDetailSerializer,
        parameters=[ID_USER],
        responses={
            201: OpenApiResponse(
                response=GuestSerializer,
                description="Успешное создание гостя",
            ),
            401: OpenApiResponse(
                response=GuestErrorAuthSerializer,
                description="Ошибка: Пользователь не авторизирован",
            ),
            404: OpenApiResponse(
                response=GuestErrorUserSerializer,
                description="Ошибка: Турист не найден",
            ),
        },
    ),
    retrieve=extend_schema(
        summary="Информация о Госте",
        description="Получение информации о Госте через идентификатор. Доступно только авторизованным пользователям.",
        parameters=[ID_USER, GUEST_ID],
        responses={
            200: OpenApiResponse(
                response=GuestSerializer,
                description="Успешное получение информации о госте",
            ),
            401: OpenApiResponse(
                response=GuestErrorAuthSerializer,
                description="Ошибка: Пользователь не авторизирован",
            ),
            404: OpenApiResponse(
                response=GuestErrorBaseSerializer,
                description="Ошибка при удалении гостя",
                examples=[
                    OpenApiExample(
                        response_only=True,
                        name="Ошибка: Гость не найден",
                        value={"detail": GUEST_ERROR},
                    ),
                    OpenApiExample(
                        response_only=True,
                        name="Ошибка: Турист не найден",
                        value={"detail": GUEST_USER_ERROR},
                    ),
                ],
            ),
        },
    ),
    update=extend_schema(
        summary="Полное обновление Гостя",
        description="Обновление всех полей Гостя. Доступно только авторизованным пользователям.",
        request=GuestDetailSerializer,
        parameters=[ID_USER, GUEST_ID],
        responses={
            200: OpenApiResponse(
                response=GuestSerializer,
                description="Гость успешно обновлен",
            ),
            401: OpenApiResponse(
                response=GuestErrorAuthSerializer,
                description="Ошибка: Пользователь не авторизирован",
            ),
            404: OpenApiResponse(
                response=GuestErrorBaseSerializer,
                description="Ошибка при удалении гостя",
                examples=[
                    OpenApiExample(
                        response_only=True,
                        name="Ошибка: Гость не найден",
                        value={"detail": GUEST_ERROR},
                    ),
                    OpenApiExample(
                        response_only=True,
                        name="Ошибка: Турист не найден",
                        value={"detail": GUEST_USER_ERROR},
                    ),
                ],
            ),
        },
    ),
    destroy=extend_schema(
        summary="Удаление Гостя",
        description="Полное удаление Гостя. Доступно только авторизованным пользователям.",
        parameters=[ID_USER, GUEST_ID],
        responses={
            204: OpenApiResponse(
                description="Гость удален",
            ),
            401: OpenApiResponse(
                response=GuestErrorAuthSerializer,
                description="Ошибка: Пользователь не авторизирован",
            ),
            404: OpenApiResponse(
                response=GuestErrorBaseSerializer,
                description="Ошибка при удалении гостя",
                examples=[
                    OpenApiExample(
                        response_only=True,
                        name="Ошибка: Гость не найден",
                        value={"detail": GUEST_ERROR},
                    ),
                    OpenApiExample(
                        response_only=True,
                        name="Ошибка: Турист не найден",
                        value={"detail": GUEST_USER_ERROR},
                    ),
                ],
            ),
        },
    ),
)
class GuestViewSet(UserRelatedViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Guest.objects.none()
    error_message = GUEST_ERROR

    def get_queryset(self):
        """Фильтрует гостей по user_id или возвращает всех для суперпользователя."""
        user = self.get_user()

        if self.request.user.is_superuser:
            if user is not None:
                return Guest.objects.filter(user_owner=user)
            return Guest.objects.all()

        self.check_permissions_for_user(user)
        return Guest.objects.filter(user_owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return GuestDetailSerializer
        return GuestSerializer

    def perform_create(self, serializer):
        user = self.get_user()
        serializer.save(user_owner=user)

    def get_object(self):
        user = self.get_user()
        try:
            return Guest.objects.select_related("user_owner").get(
                pk=self.kwargs["pk"], user_owner=user or self.request.user
            )
        except Guest.DoesNotExist:
            raise NotFound({"detail": self.error_message}) from None
