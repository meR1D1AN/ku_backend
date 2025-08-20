from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import viewsets

from all_fixture.pagination import CustomLOPagination
from all_fixture.views_fixture import (
    CALENDAR_ID,
    CALENDAR_SETTINGS,
    DISCOUNT,
    HOTEL_ID,
    LIMIT,
    OFFSET,
)
from calendars.models import CalendarDate
from calendars.serializers import CalendarDateSerializer
from hotels.models import Hotel


@extend_schema_view(
    list=extend_schema(
        summary="Календарь стоимости номеров в определённом отеле",
        description="`hotel_id` - обязательное поле, необходимо чтобы отдать список календаря у определённого отеля",
        parameters=[HOTEL_ID, LIMIT, OFFSET],
        responses={
            200: OpenApiResponse(
                CalendarDateSerializer(many=True),
                description="Успешное получение списка всех дней в календаре стоимости номеров у определённого отеля",
            ),
        },
        tags=[CALENDAR_SETTINGS["name"]],
    ),
    create=extend_schema(
        summary="Добавление нового календаря стоимости номеров в определённом отеле",
        description=(
            "`hotel_id` - обязательное поле, необходимое для создания календаря стоимости номеров в "
            "определённом отеле.\n\n"
            f"`discount_amount` - {DISCOUNT}"
        ),
        request=CalendarDateSerializer,
        parameters=[HOTEL_ID],
        responses={
            201: OpenApiResponse(
                CalendarDateSerializer,
                description="Успешное создание календаря стоимости номеров в определённом отеле",
            ),
        },
        tags=[CALENDAR_SETTINGS["name"]],
    ),
    retrieve=extend_schema(
        summary="Детали каленжаря стоимости номеров в определённом отеле",
        description="Получение информации о календаре стоимости номеров в определённом отеле",
        parameters=[HOTEL_ID, CALENDAR_ID],
        responses={
            200: OpenApiResponse(
                CalendarDateSerializer,
                description="Успешное получение календаря стоимости номеров в определённом отеле",
            ),
            404: OpenApiResponse(description="Ошибка запроса"),
        },
        tags=[CALENDAR_SETTINGS["name"]],
    ),
    update=extend_schema(
        summary="Полное обновление календаря стоимости номеров в определённом отеле",
        description="Обновление всех полей календаря стоимости номеров в определённом отеле",
        request=CalendarDateSerializer,
        parameters=[HOTEL_ID, CALENDAR_ID],
        responses={
            200: OpenApiResponse(
                CalendarDateSerializer,
                description="Успешное обновление календаря стоимости номеров в определённом отеле",
            ),
        },
        tags=[CALENDAR_SETTINGS["name"]],
    ),
    destroy=extend_schema(
        summary="Удаление календаря стоимости номеров в определённом отеле",
        description="Полное удаление календаря стоимости номеров в определённом отеле",
        parameters=[HOTEL_ID, CALENDAR_ID],
        responses={
            204: OpenApiResponse(description="Календарь удален"),
        },
        tags=[CALENDAR_SETTINGS["name"]],
    ),
)
class PriceCalendarViewSet(viewsets.ModelViewSet):
    queryset = CalendarDate.objects.none()
    serializer_class = CalendarDateSerializer
    pagination_class = CustomLOPagination

    def get_queryset(self):
        hotel_id = self.kwargs["hotel_id"]
        return CalendarDate.objects.filter(hotel_id=hotel_id)

    def perform_create(self, serializer):
        hotel = get_object_or_404(Hotel, id=self.kwargs["hotel_id"])
        serializer.save(hotel=hotel)
