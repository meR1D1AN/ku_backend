from decimal import Decimal

from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import (
    CharField,
    DateField,
    DecimalField,
    FloatField,
    IntegerField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    SlugRelatedField,
)

from all_fixture.errors.list_error import (
    DATE_ERROR,
    DECIMAL_ERROR,
    DECIMAL_INVALID,
    FLIGHT_ERROR,
    FLIGHT_FROM_ERROR,
    FLIGHT_TO_ERROR,
    HOTEL_FORMAT_ERROR,
    HOTEL_ID_ERROR,
    MIN_ERROR,
    ROOM_FORMAT_ERROR,
    ROOM_ID_ERROR,
    TOUR_MAX_PRICE_ERROR,
    TOUROPERATOR_ERROR,
    TOUROPERATOR_FORMAT_ERROR,
    TYPE_OF_MEAL_ERROR,
    TYPE_OF_MEAL_FORMAT_ERROR,
)
from flights.serializers import FlightSerializer
from hotels.serializers import HotelListWithPhotoSerializer, HotelShortSerializer
from hotels.serializers_type_of_meals import TypeOfMealSerializer
from rooms.serializers import RoomDetailSerializer
from tours.models import Tour
from tours.validators import EndDateValidator, PriceValidator, StartDateValidator


class TourSerializer(ModelSerializer):
    """
    Сериализатор для модели Tour, для ручек.
    POST, PUT.
    Создание, Обновление.
    """

    start_date = DateField(
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
        error_messages={
            "invalid": DATE_ERROR,
        },
    )
    end_date = DateField(
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
        error_messages={
            "invalid": DATE_ERROR,
        },
    )
    total_price = DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Итоговая стоимость тура",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        error_messages={
            "min_value": MIN_ERROR,
            "max_value": TOUR_MAX_PRICE_ERROR,
            "invalid": DECIMAL_ERROR,
        },
        default="150000.00",
    )
    discount_amount = DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Величина скидки",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        error_messages={
            "min_value": MIN_ERROR,
            "max_value": TOUR_MAX_PRICE_ERROR,
            "invalid": DECIMAL_ERROR,
        },
        default="5000.00",
    )
    markup_amount = DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Наценка на тур",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        error_messages={
            "min_value": MIN_ERROR,
            "max_value": TOUR_MAX_PRICE_ERROR,
            "invalid": DECIMAL_ERROR,
        },
        default="20000.00",
    )

    class Meta:
        model = Tour
        fields = (
            "id",
            "start_date",
            "end_date",
            "flight_to",
            "flight_from",
            "departure_country",
            "departure_city",
            "arrival_country",
            "arrival_city",
            "tour_operator",
            "hotel",
            "rooms",
            "type_of_meals",
            "transfer",
            "discount_amount",
            "discount_start_date",
            "discount_end_date",
            "markup_amount",
            "publish_start_date",
            "publish_end_date",
            "total_price",
            "created_at",
            "updated_at",
            "is_active",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
        )
        validators = [
            StartDateValidator(),
            EndDateValidator(),
            PriceValidator(),
        ]

        extra_kwargs = {
            "flight_to": {
                "error_messages": {
                    "does_not_exist": FLIGHT_ERROR,
                    "invalid": FLIGHT_TO_ERROR,
                }
            },
            "flight_from": {
                "error_messages": {
                    "does_not_exist": FLIGHT_ERROR,
                    "invalid": FLIGHT_FROM_ERROR,
                }
            },
            "tour_operator": {
                "error_messages": {
                    "does_not_exist": TOUROPERATOR_ERROR,
                    "invalid": TOUROPERATOR_FORMAT_ERROR,
                }
            },
            "hotel": {
                "error_messages": {
                    "does_not_exist": HOTEL_ID_ERROR,
                    "invalid": HOTEL_FORMAT_ERROR,
                }
            },
            "rooms": {
                "error_messages": {
                    "does_not_exist": ROOM_ID_ERROR,
                    "invalid": ROOM_FORMAT_ERROR,
                    "null": "Список номеров не может быть пустым.",
                    "blank": "Список номеров не может быть пустым.",
                    "not_a_list": "Ожидается список ID номеров.",
                }
            },
            "type_of_meals": {
                "error_messages": {
                    "does_not_exist": TYPE_OF_MEAL_ERROR,
                    "invalid": TYPE_OF_MEAL_FORMAT_ERROR,
                    "null": "Список типов питания не может быть пустым.",
                    "blank": "Список типов питания не может быть пустым.",
                    "not_a_list": "Ожидается список ID типов питания.",
                }
            },
        }


class TourPatchSerializer(ModelSerializer):
    """
    Сериализатор для модели Tour, для единственного действия - ставить тур в архив, и убирать его из архива.
    PATCH.
    Частичное обновление.
    """

    class Meta:
        model = Tour
        fields = ("is_active",)


class TourListSerializer(TourSerializer):
    """
    Сериализатор для модели Tour, для ручек.
    GET, GET(RETRIEVE).
    Список всех туров, детальная информация о туре.
    """

    hotel = HotelListWithPhotoSerializer()
    tour_operator = SerializerMethodField()
    flight_to = FlightSerializer()
    flight_from = FlightSerializer()
    rooms = RoomDetailSerializer(
        many=True,
        read_only=True,
    )
    type_of_meals = TypeOfMealSerializer(
        many=True,
        read_only=True,
    )

    class Meta(TourSerializer.Meta):
        fields = TourSerializer.Meta.fields

    def get_tour_operator(self, obj: Tour) -> str:
        return obj.tour_operator.company_name


class TourPopularSerializer(ModelSerializer):
    """
    Сериализатор для списка популярных туров.
    """

    photo = SerializerMethodField()
    tours_count = IntegerField(
        min_value=0,
        required=True,
    )
    total_price = DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Стоимость минимального популярного тура",
        error_messages=DECIMAL_INVALID,
        default="150000.00",
    )

    class Meta:
        model = Tour
        fields = (
            "arrival_country",
            "photo",
            "total_price",
            "tours_count",
        )

    def get_photo(self, obj) -> str:
        """
        Возвращает URL первой фотографии отеля.
        """
        request = self.context.get("request")
        first_photo = obj.hotel.hotel_photos.first()
        if first_photo:
            return request.build_absolute_uri(first_photo.photo.url) if request else first_photo.photo.url
        return None


class TourShortSerializer(ModelSerializer):
    """
    Сериализатор для списка горящих туров.
    """

    hotel = HotelShortSerializer()
    tour_operator = SlugRelatedField(
        slug_field="company_name",
        read_only=True,
    )
    guests = SerializerMethodField()
    total_price = DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Стоимость горящего тура",
        error_messages=DECIMAL_INVALID,
        default="150000.00",
    )

    class Meta:
        model = Tour
        fields = (
            "hotel",
            "total_price",
            "start_date",
            "end_date",
            "guests",
            "tour_operator",
        )

    @extend_schema_field(
        {
            "type": "string",
            "format": "string",
            "example": {
                "number_of_adults": 2,
                "number_of_children": 1,
            },
        }
    )
    def get_guests(self, obj: Tour):
        return {
            "number_of_adults": obj.number_of_adults,
            "number_of_children": obj.number_of_children,
        }


class TourFiltersRequestSerializer(Serializer):
    """Сериализатор для параметров расширенного поиска (все поля необязательные)."""

    departure_city = CharField(
        required=False,
    )
    arrival_city = CharField(
        required=False,
    )
    start_date = DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        error_messages={"invalid": "Некорректный формат даты. Используйте YYYY-MM-DD"},
    )
    nights = IntegerField(
        min_value=1,
        required=False,
    )
    guests = IntegerField(
        min_value=1,
        required=False,
    )
    city = CharField(
        required=False,
    )
    type_of_rest = CharField(
        required=False,
    )
    place = CharField(
        required=False,
    )
    price_gte = IntegerField(
        min_value=0,
        required=False,
    )
    price_lte = IntegerField(
        min_value=0,
        required=False,
    )
    user_rating = FloatField(
        min_value=0,
        max_value=10,
        required=False,
    )
    star_category = IntegerField(
        min_value=0,
        max_value=5,
        required=False,
    )
    distance_to_the_airport = IntegerField(
        min_value=0,
        required=False,
    )
    tour_operator = CharField(
        required=False,
    )
    validators = [
        StartDateValidator(),
    ]
