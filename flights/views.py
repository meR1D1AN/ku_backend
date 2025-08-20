from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.exceptions import NotFound

from all_fixture.errors.list_error import FLIGHT_ERROR
from all_fixture.errors.serializers_error import FlightErrorIdSerializer
from all_fixture.pagination import CustomLOPagination
from all_fixture.views_fixture import (
    FLIGHT_ARRIVAL_CITY,
    FLIGHT_ARRIVAL_COUNTRY,
    FLIGHT_ARRIVAL_DATE,
    FLIGHT_DEPARTURE_CITY,
    FLIGHT_DEPARTURE_COUNTRY,
    FLIGHT_DEPARTURE_DATE,
    FLIGHT_ID,
    FLIGHT_NUMBER,
    FLIGHT_SETTINGS,
    LIMIT,
    OFFSET,
)
from flights.models import Flight
from flights.serializers import FlightSerializer


@extend_schema(tags=[FLIGHT_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список рейсов",
        description="Получение списка всех рейсов",
        parameters=[
            LIMIT,
            OFFSET,
            FLIGHT_DEPARTURE_COUNTRY,
            FLIGHT_DEPARTURE_CITY,
            FLIGHT_DEPARTURE_DATE,
            FLIGHT_ARRIVAL_COUNTRY,
            FLIGHT_ARRIVAL_CITY,
            FLIGHT_ARRIVAL_DATE,
            FLIGHT_NUMBER,
        ],
        responses={
            200: OpenApiResponse(
                response=FlightSerializer(many=True),
                description="Успешное получение всех рейсов",
            ),
        },
    ),
    create=extend_schema(
        summary="Добавление рейса",
        description="Создание новой рейса",
        request={"multipart/form-data": FlightSerializer},
        responses={
            201: OpenApiResponse(
                response=FlightSerializer,
                description="Успешное создание рейса",
            ),
        },
    ),
    retrieve=extend_schema(
        summary="Информация о рейсе",
        description="Получение информации о рейсе через идентификатор",
        parameters=[FLIGHT_ID],
        responses={
            200: OpenApiResponse(
                response=FlightSerializer,
                description="Успешное получение информации о рейсе",
            ),
            404: OpenApiResponse(
                response=FlightErrorIdSerializer,
                description="Ошибка: рейс не найден",
            ),
        },
    ),
    update=extend_schema(
        summary="Полное обновление рейса",
        description="Обновление всех полей рейса",
        request=FlightSerializer,
        parameters=[FLIGHT_ID],
        responses={
            200: OpenApiResponse(
                response=FlightSerializer,
                description="Успешное обновление рейса",
            ),
            404: OpenApiResponse(
                response=FlightErrorIdSerializer,
                description="Ошибка: рейс не найден",
            ),
        },
    ),
    partial_update=extend_schema(
        summary="Частичное обновление рейса",
        description="Обновление отдельных полей рейса",
        request=FlightSerializer,
        parameters=[FLIGHT_ID],
        responses={
            200: OpenApiResponse(
                response=FlightSerializer,
                description="Успешное обновление рейса",
            ),
            404: OpenApiResponse(
                response=FlightErrorIdSerializer,
                description="Ошибка: рейс не найден",
            ),
        },
    ),
    destroy=extend_schema(
        summary="Удаление рейса",
        description="Полное удаление рейса",
        parameters=[FLIGHT_ID],
        responses={
            204: OpenApiResponse(
                description="Успешное удаление рейса",
            ),
            404: OpenApiResponse(
                response=FlightErrorIdSerializer,
                description="Ошибка: рейс не найден",
            ),
        },
    ),
)
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    pagination_class = CustomLOPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = (
        "departure_country",
        "departure_city",
        "departure_date",
        "arrival_country",
        "arrival_city",
        "arrival_date",
        "flight_number",
    )

    def get_object(self):
        try:
            return Flight.objects.get(pk=self.kwargs["pk"])
        except Flight.DoesNotExist:
            raise NotFound(FLIGHT_ERROR) from None
