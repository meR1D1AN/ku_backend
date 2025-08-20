from random import choice

from django.db.models import Count, F, Min, OuterRef, Prefetch, Q, Subquery, Window
from django.db.models.functions import RowNumber
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from all_fixture.errors.list_error import (
    HOTEL_ID_ERROR,
    PHOTO_ERROR,
    TYPE_OF_MEAL_ERROR,
)
from all_fixture.errors.serializers_error import (
    HotelBaseErrorSerializer,
    HotelErrorIdSerializer,
    HotelPhotoErrorFileSerializer,
    RoomDateErrorHotelIdSerializer,
    TypeOfMealErrorNameSerializer,
)
from all_fixture.errors.views_error import (
    HOTEL_PHOTO_DESTROY_404,
    HOTEL_UPDATE_404,
    TYPE_OF_MEAL_DESTROY_404,
    TYPE_OF_MEAL_RETRIEVE_404,
    TYPE_OF_MEAL_UPDATE_404,
)
from all_fixture.pagination import CustomLOPagination
from all_fixture.views_fixture import (
    DISCOUNT_SETTINGS,
    FILTER_CITY,
    FILTER_PLACE,
    FILTER_STAR_CATEGORY,
    FILTER_TYPE_OF_REST,
    FILTER_USER_RATING,
    HOTEL_CHECK_IN,
    HOTEL_CHECK_OUT,
    HOTEL_GUESTS,
    HOTEL_ID,
    HOTEL_ID_PHOTO,
    HOTEL_PHOTO_SETTINGS,
    HOTEL_PRICE_GTE,
    HOTEL_PRICE_LTE,
    HOTEL_SETTINGS,
    ID_HOTEL,
    LIMIT,
    OFFSET,
    TYPE_OF_MEAL_ID,
    TYPE_OF_MEAL_SETTINGS,
    WHAT_ABOUT_SETTINGS,
)
from calendars.models import CalendarPrice
from hotels.filters import HotelFilter
from hotels.models import Hotel, HotelPhoto, HotelWhatAbout, TypeOfMeal
from hotels.serializers import (
    HotelBaseSerializer,
    HotelDetailSerializer,
    HotelFiltersResponseSerializer,
    HotelListRoomAndPhotoSerializer,
    HotelPhotoSerializer,
    HotelPopularSerializer,
    HotelShortWithPriceSerializer,
    HotelWhatAboutFullSerializer,
)
from hotels.serializers_type_of_meals import TypeOfMealSerializer


class HotelRelatedViewSet(viewsets.ModelViewSet):
    hotel_lookup_field = "hotel_id"
    error_message = None

    def get_hotel(self):
        if not hasattr(self, "_hotel"):
            hotel_id = self.kwargs.get(self.hotel_lookup_field)
            try:
                return Hotel.objects.get(id=hotel_id)
            except Hotel.DoesNotExist:
                raise NotFound(HOTEL_ID_ERROR) from None
        return self._hotel

    def get_queryset(self):
        hotel = self.get_hotel()
        return self.model.objects.filter(hotel_id=hotel.id)

    def perform_create(self, serializer):
        hotel = self.get_hotel()
        serializer.save(hotel=hotel)

    def get_object(self):
        hotel = self.get_hotel()
        try:
            return self.model.objects.select_related("hotel").get(
                hotel_id=hotel.id,
                id=self.kwargs["pk"],
            )
        except self.model.DoesNotExist:
            raise NotFound(self.error_message) from None


@extend_schema(tags=[HOTEL_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список отелей",
        description="Получение списка всех отелей с пагинацией и возможностью фильтрации.",
        parameters=[
            LIMIT,
            OFFSET,
            HOTEL_CHECK_IN,
            HOTEL_CHECK_OUT,
            HOTEL_GUESTS,
            FILTER_CITY,
            FILTER_TYPE_OF_REST,
            FILTER_PLACE,
            HOTEL_PRICE_GTE,
            HOTEL_PRICE_LTE,
            FILTER_USER_RATING,
            FILTER_STAR_CATEGORY,
        ],
        responses={
            200: OpenApiResponse(
                response=HotelFiltersResponseSerializer(many=True),
                description="Успешное получение списка отелей",
            ),
        },
    ),
    create=extend_schema(
        summary="Добавление отеля",
        description="Создание нового отеля",
        request=HotelBaseSerializer,
        responses={
            201: OpenApiResponse(
                response=HotelBaseSerializer,
                description="Успешное создание отеля",
            ),
            400: OpenApiResponse(
                response=HotelBaseErrorSerializer,
                description="Ошибки при создании отеля",
                examples=[
                    OpenApiExample(
                        response_only=True,
                        name="Ошибка: Обязательное поле",
                        value={
                            "name": ["Обязательное поле."],
                        },
                    )
                ],
            ),
        },
    ),
    retrieve=extend_schema(
        summary="Детали отеля",
        description="Получение полной информации об отеле",
        parameters=[ID_HOTEL],
        responses={
            200: OpenApiResponse(
                response=HotelListRoomAndPhotoSerializer,
                description="Успешное получение отеля",
            ),
            404: OpenApiResponse(
                response=RoomDateErrorHotelIdSerializer,
                description="Ошибка: отель не найден",
            ),
        },
    ),
    update=extend_schema(
        summary="Полное обновление отеля",
        description="Обновление всех полей отеля",
        parameters=[ID_HOTEL],
        request=HotelDetailSerializer,
        responses={
            200: OpenApiResponse(
                response=HotelDetailSerializer,
                description="Успешное обновление отеля",
            ),
            400: HOTEL_UPDATE_404,
            404: OpenApiResponse(
                response=RoomDateErrorHotelIdSerializer,
                description="Ошибка: Отель не найден",
            ),
        },
    ),
    destroy=extend_schema(
        summary="Удаление отеля",
        description="Полное удаление отеля",
        parameters=[ID_HOTEL],
        responses={
            204: OpenApiResponse(
                description="Успешное удаление отеля",
            ),
            404: OpenApiResponse(
                response=RoomDateErrorHotelIdSerializer,
                description="Ошибка: Отель не найден",
            ),
        },
    ),
)
class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    pagination_class = CustomLOPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = HotelFilter

    def get_serializer_class(self):
        if self.action == "list":
            return HotelFiltersResponseSerializer
        elif self.action == "retrieve":
            return HotelListRoomAndPhotoSerializer
        elif self.action == "create":
            return HotelBaseSerializer
        else:
            return HotelDetailSerializer

    def get_serializer_context(self):
        """Передача контекста в сериализатор для фильтрации."""
        context = super().get_serializer_context()
        if self.action == "list":
            context.update(
                {
                    "guests": self.request.query_params.get("guests", 1),
                    "check_in_date": self.request.query_params.get(
                        "check_in_date",
                        None,
                    ),
                    "check_out_date": self.request.query_params.get(
                        "check_out_date",
                        None,
                    ),
                }
            )
        return context

    def get_queryset(self):
        """Применение фильтров и оптимизация запросов к списку отелей."""
        queryset = super().get_queryset()

        # Оптимизируем запрос, если действие требует получения фотографий
        if self.action in ["list", "retrieve"]:
            queryset = queryset.prefetch_related("hotel_photos")

        if self.action == "list":
            filterset = self.filterset_class(
                self.request.query_params,
                queryset=queryset,
            )
            if not filterset.is_valid():
                return Response(
                    {"errors": filterset.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return filterset.qs
        return queryset

    def get_object(self):
        """Оптимизация запроса для получения одного отеля с фотографиями."""
        queryset = self.get_queryset()
        try:
            return queryset.get(id=self.kwargs["pk"])
        except Hotel.DoesNotExist:
            raise NotFound(HOTEL_ID_ERROR) from None


@extend_schema(tags=[DISCOUNT_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список отелей по специальной цене",
        description="Получение списка всех отелей по специальной цене",
        parameters=[LIMIT, OFFSET],
        responses={
            200: HotelShortWithPriceSerializer(many=True),
        },
    )
)
class HotelsHotView(viewsets.ModelViewSet):
    """Отели по специальной цене."""

    serializer_class = HotelShortWithPriceSerializer
    pagination_class = CustomLOPagination
    queryset = Hotel.objects.none()

    def get_queryset(self):
        """Получение запроса с отелями по одному из каждой страны с минимальной ценой."""
        min_price_subquery = (
            CalendarPrice.objects.filter(
                calendar_date__discount=True,
                calendar_date__available_for_booking=True,
                room__hotel=OuterRef("pk"),
            )
            .order_by("price")
            .values("price")[:1]
        )

        queryset = (
            Hotel.objects.filter(is_active=True)
            .prefetch_related("hotel_photos")
            .annotate(min_price=Subquery(min_price_subquery))
            .exclude(min_price=None)
            .annotate(
                grouped_countries=Window(
                    expression=RowNumber(),
                    partition_by=[F("country")],
                    order_by=F("min_price").asc(),
                )
            )
            .filter(grouped_countries=1)
            .order_by("country")
        )

        return queryset


@extend_schema(tags=[DISCOUNT_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список популярных отелей",
        description="Получение списка шести популярных отелей",
        parameters=[LIMIT, OFFSET],
        responses={
            200: HotelPopularSerializer(many=True),
        },
    )
)
class HotelsPopularView(viewsets.ModelViewSet):
    """Отели шести стран."""

    serializer_class = HotelPopularSerializer
    pagination_class = CustomLOPagination
    queryset = Hotel.objects.none()

    def get_queryset(self):
        """Получение запроса с отелями по одному из шести стран с минимальной ценой."""

        today = timezone.now().date()
        min_price_without_discount_subquery = (
            CalendarPrice.objects.filter(
                calendar_date__available_for_booking=True,
                calendar_date__start_date__gte=today,
                room__hotel=OuterRef("pk"),
            )
            .order_by("price")
            .values("price")[:1]
        )
        country_hotel_count = (
            Hotel.objects.filter(is_active=True, country=OuterRef("country"))
            .values("country")
            .annotate(count=Count("id"))
            .values("count")
        )
        queryset = (
            Hotel.objects.filter(is_active=True)
            .prefetch_related("hotel_photos")
            .annotate(
                hotels_count=Subquery(country_hotel_count),
                min_price_without_discount=Subquery(min_price_without_discount_subquery),
            )
            .exclude(min_price_without_discount=None)
            .annotate(
                grouped_countries=Window(
                    expression=RowNumber(),
                    partition_by=[F("country")],
                    order_by=F("min_price_without_discount").asc(),
                )
            )
            .filter(grouped_countries=1)
            .order_by("min_price_without_discount")[:6]
        )

        return queryset


@extend_schema(tags=[HOTEL_PHOTO_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список типов фотографий отеля",
        description="Получение списка всех фотографий отеля",
        parameters=[HOTEL_ID],
        responses={
            200: OpenApiResponse(
                response=HotelPhotoSerializer(many=True),
                description="Успешное получение всех фотографий отеля",
            ),
            404: OpenApiResponse(
                response=HotelErrorIdSerializer,
                description="Ошибка: Отель не найден",
            ),
        },
    ),
    create=extend_schema(
        summary="Добавление фотографий отеля",
        description="Создание новых фотографий отеля",
        parameters=[HOTEL_ID],
        request={
            "multipart/form-data": HotelPhotoSerializer,
        },
        responses={
            201: OpenApiResponse(
                response=HotelPhotoSerializer,
                description="Успешное создание фотографии в отеле",
            ),
            400: OpenApiResponse(
                response=HotelPhotoErrorFileSerializer,
                description="Ошибка: Загрузки фотографии в отеле",
            ),
            404: OpenApiResponse(
                response=HotelErrorIdSerializer,
                description="Ошибка: Отель не найден",
            ),
        },
    ),
    destroy=extend_schema(
        summary="Удаление фотографий отеля",
        description="Полное удаление фотографий отеля",
        parameters=[HOTEL_ID, HOTEL_ID_PHOTO],
        responses={
            204: OpenApiResponse(
                description="Фотография в отеле удалена",
            ),
            404: HOTEL_PHOTO_DESTROY_404,
        },
    ),
)
class HotelPhotoViewSet(HotelRelatedViewSet):
    model = HotelPhoto
    queryset = HotelPhoto.objects.none()
    serializer_class = HotelPhotoSerializer
    error_message = PHOTO_ERROR


@extend_schema(tags=[TYPE_OF_MEAL_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список типов питания в определённом отеле",
        description="Получение списка всех типов питания в определённом отеле",
        parameters=[HOTEL_ID],
        responses={
            200: OpenApiResponse(
                response=TypeOfMealSerializer(many=True),
                description="Успешное получение типов питания в отеле",
            ),
            404: OpenApiResponse(
                response=HotelErrorIdSerializer,
                description="Ошибка: Отель не найден",
            ),
        },
    ),
    create=extend_schema(
        summary="Добавление типа питания в определённый отель",
        description="Создание нового типа питания в определённом отеле",
        parameters=[HOTEL_ID],
        request={
            "multipart/form-data": TypeOfMealSerializer,
        },
        responses={
            201: OpenApiResponse(
                response=TypeOfMealSerializer,
                description="Успешное создание типа питания в отеле",
            ),
            400: OpenApiResponse(
                response=TypeOfMealErrorNameSerializer,
                description="Ошибка: Создания типа питания в отеле",
            ),
            404: OpenApiResponse(
                response=HotelErrorIdSerializer,
                description="Ошибка: Отель не найден",
            ),
        },
    ),
    retrieve=extend_schema(
        summary="Получение типа питания в определённом отеле",
        description="Получение типа питания в определённом отеле",
        parameters=[HOTEL_ID, TYPE_OF_MEAL_ID],
        responses={
            200: OpenApiResponse(
                response=TypeOfMealSerializer,
                description="Успешное получение типа питания в отеле",
            ),
            404: TYPE_OF_MEAL_RETRIEVE_404,
        },
    ),
    update=extend_schema(
        summary="Полное обновление типа питания в определённом отеле",
        description="Обновление всех полей типа питания в определённом отеле",
        request={
            "multipart/form-data": TypeOfMealSerializer,
        },
        parameters=[HOTEL_ID, TYPE_OF_MEAL_ID],
        responses={
            200: OpenApiResponse(
                response=TypeOfMealSerializer,
                description="Успешное обновление типа питания в отеле",
            ),
            404: TYPE_OF_MEAL_UPDATE_404,
        },
    ),
    destroy=extend_schema(
        summary="Удаление типа питания в определённом отеле",
        description="Полное удаление типа питания в определённом отеле",
        parameters=[HOTEL_ID, TYPE_OF_MEAL_ID],
        responses={
            204: OpenApiResponse(
                description="Тип питания в отеле удален",
            ),
            404: TYPE_OF_MEAL_DESTROY_404,
        },
    ),
)
class TypeOfMealViewSet(HotelRelatedViewSet):
    model = TypeOfMeal
    queryset = TypeOfMeal.objects.none()
    serializer_class = TypeOfMealSerializer
    error_message = TYPE_OF_MEAL_ERROR


@extend_schema(tags=[WHAT_ABOUT_SETTINGS["name"]])
@extend_schema_view(
    list=extend_schema(
        summary="Список подборок что насчёт ...",
        description="Получение списка подборок что насчёт ...",
        responses={
            200: OpenApiResponse(
                response=HotelWhatAboutFullSerializer(many=True),
                description="Успешное получение списка подборок",
            ),
        },
    )
)
class HotelWarpUpViewSet(viewsets.ModelViewSet):
    queryset = HotelWhatAbout.objects.none()
    serializer_class = HotelWhatAboutFullSerializer

    def get_queryset(self):
        """
        Возвращает случайную подборку отелей с минимальными ценами,
        начиная с текущей даты, с учетом скидок
        """
        today = timezone.now().date()
        all_ids = list(HotelWhatAbout.objects.values_list("id", flat=True))
        if not all_ids:
            return HotelWhatAbout.objects.none()

        # Выбираем случайную подборку
        random_id = choice(all_ids)

        # Находим минимальную цену, начиная с текущей даты
        # Без ограничения по конечной дате
        hotels_with_prices = Hotel.objects.annotate(
            min_price_without_discount=Min(
                "calendar_dates__calendar_prices__price",
                filter=Q(calendar_dates__start_date__gte=today, calendar_dates__calendar_prices__price__gt=0),
            ),
        )
        # Создаем префетч для оптимизации запросов
        prefetch = Prefetch("hotel", queryset=hotels_with_prices)

        # Возвращаем подборку с префетчем отелей и их ценами
        return HotelWhatAbout.objects.filter(id=random_id).prefetch_related(prefetch)
