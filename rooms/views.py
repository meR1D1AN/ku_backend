from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework.exceptions import NotFound

from all_fixture.errors.list_error import (
    HOTEL_ID_ERROR,
    PHOTO_ERROR,
    ROOM_ID_ERROR,
    RULE_ROOM_ERROR,
)
from all_fixture.errors.serializers_error import (
    RoomDateErrorHotelIdSerializer,
    RoomErrorIdSerializer,
    RoomPhotoErrorFileSerializer,
)
from all_fixture.errors.views_error import (
    ROOM_CREATE_400,
    ROOM_DESTROY_404,
    ROOM_PHOTO_CREATE_404,
    ROOM_PHOTO_DESTROY_404,
    ROOM_RETRIEVE_404,
    ROOM_UPDATE_400,
    ROOM_UPDATE_404,
)
from all_fixture.pagination import CustomLOPagination
from all_fixture.views_fixture import (
    HOTEL_ID,
    ID_ROOM,
    LIMIT,
    OFFSET,
    ROOM_ID,
    ROOM_ID_PHOTO,
    ROOM_PHOTO_SETTINGS,
    ROOM_RULES_SETTINGS,
    ROOM_SETTINGS,
)
from hotels.models import Hotel
from rooms.filters import RoomFilter
from rooms.models import Room, RoomPhoto, RoomRules
from rooms.serializers import (
    RoomBaseSerializer,
    RoomDetailSerializer,
    RoomPhotoSerializer,
    RoomRulesSerializer,
)


class BaseErrorHandlingMixin:
    """
    Базовый миксин для обработки ошибок 404.
    """

    error_message = None

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            if not self.error_message:
                raise
            raise NotFound(self.error_message) from None


class HotelRelatedMixin:
    """
    Примесь для проверки существования отеля перед выполнением действий.
    """

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        hotel_id = self.kwargs.get("hotel_id")
        if not Hotel.objects.filter(id=hotel_id).exists():
            raise NotFound(HOTEL_ID_ERROR)


class RoomRelatedViewSet(BaseErrorHandlingMixin, viewsets.ModelViewSet):
    """
    Базовый ViewSet для сущностей, связанных с номером.
    """

    roomd_lookup_field = "room_id"
    error_message = None

    def get_room(self):
        if not hasattr(self, "_room"):
            room_id = self.kwargs.get(self.roomd_lookup_field)
            try:
                return Room.objects.get(id=room_id)
            except Room.DoesNotExist:
                raise NotFound(ROOM_ID_ERROR) from None
        return self._room

    def get_queryset(self):
        room = self.get_room()
        return self.model.objects.filter(room_id=room.id)

    def perform_create(self, serializer):
        room = self.get_room()
        serializer.save(room=room)

    def get_object(self):
        room = self.get_room()
        try:
            return self.model.objects.select_related("room").get(
                room_id=room.id,
                id=self.kwargs["pk"],
            )
        except self.model.DoesNotExist:
            raise NotFound(self.error_message) from None


@extend_schema(tags=[ROOM_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список номеров в отеле",
        description="Получение списка всех номеров с пагинацией в отеле",
        parameters=[HOTEL_ID, LIMIT, OFFSET],
        responses={
            200: OpenApiResponse(
                response=RoomDetailSerializer(many=True),
                description="Успешное получение списка номеров в отеле",
            ),
            404: OpenApiResponse(
                response=RoomDateErrorHotelIdSerializer,
                description="Ошибка: Отель не найден",
            ),
        },
    ),
    create=extend_schema(
        summary="Добавление номера в отель",
        description="Создание нового номера в отеле",
        request=RoomBaseSerializer,
        parameters=[HOTEL_ID],
        responses={
            201: OpenApiResponse(
                response=RoomBaseSerializer,
                description="Успешное создание номера в отеле",
            ),
            400: ROOM_CREATE_400,
            404: OpenApiResponse(
                response=RoomDateErrorHotelIdSerializer,
                description="Ошибка: Отель не найден",
            ),
        },
    ),
    retrieve=extend_schema(
        summary="Детали номера",
        description="Получение информации о номере",
        parameters=[HOTEL_ID, ID_ROOM],
        responses={
            200: OpenApiResponse(
                response=RoomDetailSerializer,
                description="Успешное получение информации о номера в отеле",
            ),
            404: ROOM_RETRIEVE_404,
        },
    ),
    update=extend_schema(
        summary="Полное обновление номера в отеле",
        description="Обновление всех полей номера в отеле",
        request=RoomBaseSerializer,
        parameters=[HOTEL_ID, ID_ROOM],
        responses={
            200: OpenApiResponse(
                response=RoomBaseSerializer,
                description="Успешное обновление номера в отеле",
            ),
            400: ROOM_UPDATE_400,
            404: ROOM_UPDATE_404,
        },
    ),
    destroy=extend_schema(
        summary="Удаление номера в отеле",
        description="Полное удаление номера в отеле",
        parameters=[HOTEL_ID, ID_ROOM],
        responses={
            204: OpenApiResponse(
                description="Успешное удаление номера в отеле",
            ),
            404: ROOM_DESTROY_404,
        },
    ),
)
class RoomViewSet(HotelRelatedMixin, BaseErrorHandlingMixin, viewsets.ModelViewSet):
    """
    ViewSet для работы с номерами отеля.
    """

    queryset = Room.objects.none()
    pagination_class = CustomLOPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomFilter
    error_message = ROOM_ID_ERROR

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RoomBaseSerializer
        return RoomDetailSerializer

    def get_queryset(self):
        return Room.objects.filter(hotel_id=self.kwargs["hotel_id"]).prefetch_related(
            "room_photos",
            "rules",
        )

    def perform_create(self, serializer):
        hotel = get_object_or_404(Hotel, id=self.kwargs["hotel_id"])
        serializer.save(hotel=hotel)


@extend_schema(tags=[ROOM_PHOTO_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список фотографий номера",
        description="Получение списка всех фотографий номера с пагинацией",
        parameters=[ROOM_ID],
        responses={
            200: OpenApiResponse(
                response=RoomPhotoSerializer(many=True),
                description="Успешное получение всех фотографий номера",
            ),
            404: OpenApiResponse(
                response=RoomErrorIdSerializer,
                description="Ошибка: номер не найден",
            ),
        },
    ),
    create=extend_schema(
        summary="Добавление фотографии номера",
        description="Создание новой фотографии номера",
        parameters=[ROOM_ID],
        request={
            "multipart/form-data": RoomPhotoSerializer,
        },
        responses={
            201: OpenApiResponse(
                response=RoomPhotoSerializer,
                description="Успешное создание фотографии в номере",
            ),
            400: OpenApiResponse(
                response=RoomPhotoErrorFileSerializer,
                description="Ошибка: при загрузке фотографии",
            ),
            404: ROOM_PHOTO_CREATE_404,
        },
    ),
    destroy=extend_schema(
        summary="Удаление фотографии номера",
        description="Полное удаление фотографии номера",
        parameters=[ROOM_ID, ROOM_ID_PHOTO],
        responses={
            204: OpenApiResponse(description="Фотография в номере удалена"),
            404: ROOM_PHOTO_DESTROY_404,
        },
    ),
)
class RoomPhotoViewSet(RoomRelatedViewSet):
    """
    ViewSet для работы с фотографиями номеров.
    """

    model = RoomPhoto
    queryset = RoomPhoto.objects.none()
    serializer_class = RoomPhotoSerializer
    error_message = PHOTO_ERROR


@extend_schema(tags=[ROOM_RULES_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список правил в номере",
        description="Получение списка всех правил в номере с пагинацией",
        parameters=[LIMIT, OFFSET],
        responses={
            200: OpenApiResponse(
                response=RoomRulesSerializer(many=True),
                description="Успешное получение списка всех правил",
            ),
            400: OpenApiResponse(description="Ошибка запроса"),
        },
    ),
    create=extend_schema(
        summary="Добавление правила в номер",
        description="Создание нового правила в номере",
        parameters=[ROOM_ID],
        request={
            "multipart/form-data": RoomRulesSerializer,
        },
        responses={
            201: OpenApiResponse(
                response=RoomRulesSerializer,
                description="Успешное добавление правил в номер",
            ),
            400: OpenApiResponse(
                description="Ошибка запроса",
            ),
        },
    ),
    destroy=extend_schema(
        summary="Удаление правила в номере",
        description="Полное удаление правила в номере",
        parameters=[ROOM_ID],
        responses={
            204: OpenApiResponse(
                description="Правило в номере удалено",
            ),
            404: OpenApiResponse(
                description="Правило в номере не найдено",
            ),
        },
    ),
)
class RoomRulesViewSet(BaseErrorHandlingMixin, viewsets.ModelViewSet):
    """
    ViewSet для работы с правилами номеров.
    """

    queryset = RoomRules.objects.all()
    serializer_class = RoomRulesSerializer
    error_message = RULE_ROOM_ERROR

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
