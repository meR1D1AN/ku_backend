from dal import autocomplete
from django.db.models import Count, F, OuterRef, Subquery, Window
from django.db.models.functions import RowNumber
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework.exceptions import NotFound, ValidationError

from all_fixture.errors.list_error import TOUR_ERROR
from all_fixture.errors.serializers_error import TourErrorSerializer
from all_fixture.errors.views_descriptions import DESCRIPTION_POPULAR_TOURS
from all_fixture.errors.views_error import (
    TOUR_CREATE_400,
    TOUR_UPDATE_400,
)
from all_fixture.pagination import CustomLOPagination
from all_fixture.views_fixture import (
    DISCOUNT_SETTINGS,
    LIMIT,
    OFFSET,
    TOUR_ID,
    TOUR_SETTINGS,
)
from calendars.models import CalendarPrice
from hotels.models import Hotel, TypeOfMeal
from rooms.models import Room
from tours.filters import TourFilter
from tours.models import Tour
from tours.serializers import (
    TourListSerializer,
    TourPatchSerializer,
    TourPopularSerializer,
    TourSerializer,
    TourShortSerializer,
)


@extend_schema(tags=[TOUR_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список туров",
        description="Получение списка всех туров с пагинацией и возможностью фильтрации.",
        parameters=[
            LIMIT,
            OFFSET,
        ],
        responses={
            200: OpenApiResponse(
                response=TourShortSerializer(many=True),
                description="Успешное получение списка туров",
            )
        },
    ),
    create=extend_schema(
        summary="Добавление тура",
        description="Создание нового тура",
        request=TourSerializer,
        responses={
            201: OpenApiResponse(
                response=TourSerializer,
                description="Успешное создание тура",
            ),
            400: TOUR_CREATE_400,
            404: OpenApiResponse(
                response=TourErrorSerializer,
                description="Ошибка: Тур не найден",
            ),
        },
    ),
    retrieve=extend_schema(
        summary="Информация о туре",
        description="Получение информации о туре через идентификатор",
        parameters=[TOUR_ID],
        responses={
            200: OpenApiResponse(
                response=TourListSerializer,
                description="Успешное получение информации о туре",
            ),
            404: OpenApiResponse(
                response=TourErrorSerializer,
                description="Ошибка: Тур не найден",
            ),
        },
    ),
    update=extend_schema(
        summary="Полное обновление тура",
        description="Обновление всех полей тура",
        request=TourSerializer,
        parameters=[TOUR_ID],
        responses={
            200: OpenApiResponse(
                response=TourSerializer,
                description="Успешное обновление тура",
            ),
            400: TOUR_UPDATE_400,
            404: OpenApiResponse(
                response=TourErrorSerializer,
                description="Ошибка: Тур не найден",
            ),
        },
    ),
    partial_update=extend_schema(
        summary="Частичное обновление тура",
        description="Обновление отдельных полей тура",
        request=TourPatchSerializer,
        parameters=[TOUR_ID],
        responses={
            200: OpenApiResponse(
                response=TourPatchSerializer,
                description="Успешное обновление тура",
            ),
            404: OpenApiResponse(
                response=TourErrorSerializer,
                description="Ошибка: Тур не найден",
            ),
        },
    ),
    destroy=extend_schema(
        summary="Удаление тура",
        description="Полное удаление тура",
        parameters=[TOUR_ID],
        responses={
            204: OpenApiResponse(
                description="Успешное удаление тура",
            ),
            404: OpenApiResponse(
                response=TourErrorSerializer,
                description="Ошибка: Тур не найден",
            ),
        },
    ),
)
class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all()
    pagination_class = CustomLOPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TourFilter

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия и параметров запроса."""
        if self.action == "list":
            return TourShortSerializer
        elif self.action == "retrieve":
            return TourListSerializer
        elif self.action == "partial_update":
            return TourPatchSerializer
        else:
            return TourSerializer

    def get_queryset(self):
        """Базовый queryset с оптимизациями + поддержка фильтров."""
        queryset = super().get_queryset().select_related("hotel").prefetch_related("hotel__hotel_photos")
        if self.action == "list":
            filterset = self.filterset_class(self.request.query_params, queryset=queryset)
            if not filterset.is_valid():
                raise ValidationError(filterset.errors)
            queryset = filterset.qs

        return queryset.distinct()

    def get_object(self):
        try:
            return Tour.objects.get(pk=self.kwargs["pk"])
        except Tour.DoesNotExist:
            raise NotFound(TOUR_ERROR) from None


@extend_schema(tags=[DISCOUNT_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список горящих туров",
        description="Получение списка всех горящих туров",
        parameters=[LIMIT, OFFSET],
        responses={
            200: TourShortSerializer(many=True),
        },
    )
)
class TourHotView(viewsets.ModelViewSet):
    """Горящие туры по одному из каждой страны по минимальной цене."""

    queryset = Tour.objects.none()
    serializer_class = TourShortSerializer
    pagination_class = CustomLOPagination

    def get_queryset(self):
        """Получение тура по одному из каждой страны с минимальной ценой."""
        guests_subquery = (
            CalendarPrice.objects.filter(
                calendar_date__discount=True,
                calendar_date__available_for_booking=True,
                room__tours=OuterRef("pk"),
            )
            .order_by("price")
            .values("room__number_of_adults", "room__number_of_children")[:1]
        )

        queryset = (
            Tour.objects.filter(is_active=True, discount_amount__isnull=False)
            .annotate(
                number_of_adults=Subquery(guests_subquery.values("room__number_of_adults")),
                number_of_children=Subquery(guests_subquery.values("room__number_of_children")),
                country_rank=Window(
                    expression=RowNumber(),
                    partition_by=[F("arrival_country")],
                    order_by=F("total_price").asc(),
                ),
            )
            .filter(country_rank=1)
            .order_by("arrival_country")
        )

        return queryset


@extend_schema(tags=[DISCOUNT_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список популярных туров",
        description=DESCRIPTION_POPULAR_TOURS,
        parameters=[LIMIT, OFFSET],
        responses={
            200: TourPopularSerializer(many=True),
        },
    ),
    retrieve=extend_schema(exclude=True),
)
class TourPopularView(viewsets.ModelViewSet):
    """Туры шести стран."""

    queryset = Tour.objects.none()
    serializer_class = TourPopularSerializer
    pagination_class = CustomLOPagination

    def get_queryset(self):
        """Получение тура по одному из шести страны с минимальной ценой."""

        country_tour_count = (
            Tour.objects.filter(
                is_active=True,
                arrival_country=OuterRef("arrival_country"),
            )
            .values("arrival_country")
            .annotate(count=Count("id"))
            .values("count")
        )

        queryset = (
            Tour.objects.filter(is_active=True)
            .annotate(
                tours_count=Subquery(country_tour_count),
                country_rank=Window(
                    expression=RowNumber(),
                    partition_by=[F("arrival_country")],
                    order_by=F("total_price").asc(),
                ),
            )
            .filter(country_rank=1)
            .order_by("total_price")
        )

        return queryset


class ToursAutocompleteHotel(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Hotel.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class ToursAutocompleteRoom(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Room.objects.all()
        hotel = self.forwarded.get("hotel", None)
        if hotel:
            qs = qs.filter(hotel_id=hotel)
        selected = self.forwarded.get("rooms", [])
        if selected:
            qs = qs.exclude(id__in=selected)
        if self.q:
            qs = qs.filter(category__icontains=self.q)
        return qs


class ToursAutocompleteTypeOfMeal(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = TypeOfMeal.objects.all()
        hotel = self.forwarded.get("hotel", None)
        if hotel:
            qs = qs.filter(hotel_id=hotel)
        selected = self.forwarded.get("type_of_meals", [])
        if selected:
            qs = qs.exclude(id__in=selected)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.order_by("price")
