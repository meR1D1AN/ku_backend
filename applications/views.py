from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.exceptions import NotFound

from all_fixture.errors.list_error import (
    APPLICATION_HOTEL_ERROR,
    APPLICATION_TOUR_ERROR,
)
from all_fixture.errors.serializers_error import (
    ApplicationHotelErrorIdSerializer,
    ApplicationTourErrorIdSerializer,
)
from all_fixture.pagination import CustomLOPagination
from all_fixture.views_fixture import (
    APPLICATION_ID,
    APPLICATION_SETTINGS,
    LIMIT,
    OFFSET,
)
from applications.models import ApplicationHotel, ApplicationTour
from applications.serializers import (
    ApplicationHotelListSerializer,
    ApplicationHotelSerializer,
    ApplicationTourListSerializer,
    ApplicationTourSerializer,
)


class ApplicationBaseViewSet(viewsets.ModelViewSet):
    def get_object(self):
        try:
            return self.model.objects.get(pk=self.kwargs["pk"])
        except self.model.DoesNotExist:
            raise NotFound(self.error_message) from None


@extend_schema(tags=[APPLICATION_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список заявок на тур",
        description="Получение списка всех заявок на тур",
        parameters=[LIMIT, OFFSET],
        responses={
            200: OpenApiResponse(
                response=ApplicationTourListSerializer(many=True),
                description="Успешное получение заявок на тур",
            ),
        },
    ),
    create=extend_schema(
        summary="Добавление заявки на тур",
        description="Создание новой заявки на тур",
        request=ApplicationTourSerializer,
        responses={
            201: OpenApiResponse(
                response=ApplicationTourListSerializer,
                description="Успешное создание заявки на тур",
            ),
        },
    ),
    retrieve=extend_schema(
        summary="Информация о заявке на тур",
        description="Получение информации о заявке на тур через идентификатор",
        parameters=[APPLICATION_ID],
        responses={
            200: OpenApiResponse(
                response=ApplicationTourListSerializer,
                description="Успешное получение заявки на тур",
            ),
            404: OpenApiResponse(
                response=ApplicationTourErrorIdSerializer,
                description="Ошибка: заявка на тур не найдена",
            ),
        },
    ),
    update=extend_schema(
        summary="Полное обновление заявки на тур",
        description="Обновление всех полей заявки",
        request=ApplicationTourSerializer,
        parameters=[APPLICATION_ID],
        responses={
            200: OpenApiResponse(
                response=ApplicationTourSerializer,
                description="Успешное обновление заявки на тур",
            ),
            404: OpenApiResponse(
                response=ApplicationTourErrorIdSerializer,
                description="Ошибка: заявка на тур не найдена",
            ),
        },
    ),
    destroy=extend_schema(
        summary="Удаление заявки на тур",
        description="Полное удаление заявки на тур",
        parameters=[APPLICATION_ID],
        responses={
            204: OpenApiResponse(
                description="Успешное удаление заявки на тур",
            ),
            404: OpenApiResponse(
                response=ApplicationTourErrorIdSerializer,
                description="Ошибка: заявка на тур не найдена",
            ),
        },
    ),
)
class ApplicationTourViewSet(ApplicationBaseViewSet):
    queryset = ApplicationTour.objects.all()
    pagination_class = CustomLOPagination
    model = ApplicationTour
    error_message = APPLICATION_TOUR_ERROR

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ApplicationTourSerializer
        return ApplicationTourListSerializer


@extend_schema(tags=[APPLICATION_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список заявок на отель",
        description="Получение списка заявок на отель",
        parameters=[LIMIT, OFFSET],
        responses={
            200: OpenApiResponse(
                response=ApplicationHotelListSerializer(many=True),
                description="Успешное получение заявок на отель",
            ),
        },
    ),
    create=extend_schema(
        summary="Добавление заявки на отель",
        description="Создание новой заявки на отель",
        request=ApplicationHotelSerializer,
        responses={
            201: OpenApiResponse(
                response=ApplicationHotelSerializer,
                description="Заявка на отель создана",
            ),
        },
    ),
    retrieve=extend_schema(
        summary="Информация о заявке на отель",
        description="Получение информации о заявке на отель через идентификатор",
        parameters=[APPLICATION_ID],
        responses={
            200: OpenApiResponse(
                response=ApplicationHotelListSerializer,
                description="Успешное получение заявки на отель",
            ),
            404: OpenApiResponse(
                response=ApplicationHotelErrorIdSerializer,
                description="Заявка на отель не найдена",
            ),
        },
    ),
    update=extend_schema(
        summary="Полное обновление заявки на отель",
        description="Обновление всех полей заявки на отель",
        request=ApplicationHotelSerializer,
        parameters=[APPLICATION_ID],
        responses={
            200: OpenApiResponse(
                response=ApplicationHotelSerializer,
                description="Заявка на отель обновлена",
            ),
            404: OpenApiResponse(
                response=ApplicationHotelErrorIdSerializer,
                description="Заявка на отель не найдена",
            ),
        },
    ),
    destroy=extend_schema(
        summary="Удаление заявки на отель",
        description="Полное удаление заявки на отель",
        parameters=[APPLICATION_ID],
        responses={
            204: OpenApiResponse(
                description="Заявка удалена",
            ),
            404: OpenApiResponse(
                response=ApplicationHotelErrorIdSerializer,
                description="Заявка на отель не найдена",
            ),
        },
    ),
)
class ApplicationHotelViewSet(ApplicationBaseViewSet):
    queryset = ApplicationHotel.objects.all()
    pagination_class = CustomLOPagination
    model = ApplicationHotel
    error_message = APPLICATION_HOTEL_ERROR

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ApplicationHotelSerializer
        return ApplicationHotelListSerializer
