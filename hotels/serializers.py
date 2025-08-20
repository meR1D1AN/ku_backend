from datetime import datetime
from decimal import Decimal

from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework.fields import TimeField
from rest_framework.serializers import (
    CharField,
    DateField,
    DecimalField,
    FloatField,
    ImageField,
    IntegerField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)

from all_fixture.errors.list_error import (
    HOTEL_LONGITUDE_MAX_ERROR,
    HOTEL_LONGITUDE_MIN_ERROR,
    HOTEL_MAX_DISTANCE_ERROR,
    HOTEL_MAX_STAR_ERROR,
    HOTEL_RATING_MAX_ERROR,
    HOTEL_RATING_MIN_ERROR,
    HOTEL_WIDTH_MAX_ERROR,
    HOTEL_WIDTH_MIN_ERROR,
    MIN_ERROR,
    TIME_ERROR,
)
from hotels.models import Hotel, HotelPhoto, HotelRules, HotelWhatAbout
from hotels.validators import DateValidator
from rooms.serializers import RoomDetailSerializer


class HotelBaseSerializer(ModelSerializer):
    """
    Базовая сериализация для создания отеля
    Метод POST (create).
    """

    class Meta:
        model = Hotel
        fields = (
            "id",
            "name",
        )

    def create(self, validated_data):
        return Hotel.objects.create(**validated_data)


class HotelRulesSerializer(ModelSerializer):
    """
    Сериализатор правил в отеле.
    """

    class Meta:
        model = HotelRules
        fields = (
            "name",
            "description",
        )


class HotelDetailSerializer(ModelSerializer):
    """
    Сериализация для обновления всех полей отеля
    Метод PUT, DELETE, PATCH - но его не используем, позже будет отдельная сериализация
    по добавлению отеля в архив методом PATCH.
    """

    rules = HotelRulesSerializer(
        many=True,
        source="hotels_rules",
        required=False,
    )
    star_category = IntegerField(
        required=False,
        min_value=0,
        max_value=5,
        error_messages={
            "min_value": MIN_ERROR,
            "max_value": HOTEL_MAX_STAR_ERROR,
        },
    )
    user_rating = FloatField(
        required=False,
        min_value=Decimal("0.0"),
        max_value=Decimal("10.0"),
        error_messages={
            "min_value": HOTEL_RATING_MIN_ERROR,
            "max_value": HOTEL_RATING_MAX_ERROR,
        },
    )
    width = FloatField(
        required=False,
        min_value=Decimal("-90.0"),
        max_value=Decimal("90.0"),
        error_messages={
            "min_value": HOTEL_WIDTH_MIN_ERROR,
            "max_value": HOTEL_WIDTH_MAX_ERROR,
        },
        default="55.980955",
    )
    longitude = FloatField(
        required=False,
        min_value=Decimal("-180.0"),
        max_value=Decimal("180.0"),
        error_messages={
            "min_value": HOTEL_LONGITUDE_MIN_ERROR,
            "max_value": HOTEL_LONGITUDE_MAX_ERROR,
        },
        default="37.409003",
    )
    check_in_time = TimeField(
        input_formats=["%H:%M"],
        format="%H:%M",
        error_messages={
            "invalid": TIME_ERROR,
        },
        default="14:00",
    )
    check_out_time = TimeField(
        input_formats=["%H:%M"],
        format="%H:%M",
        error_messages={
            "invalid": TIME_ERROR,
        },
        default="12:00",
    )
    distance_to_the_station = IntegerField(
        required=False,
        min_value=0,
        max_value=200000,
        error_messages={
            "min_value": MIN_ERROR,
            "max_value": HOTEL_MAX_DISTANCE_ERROR,
        },
    )
    distance_to_the_sea = IntegerField(
        required=False,
        min_value=0,
        max_value=200000,
        error_messages={
            "min_value": MIN_ERROR,
            "max_value": HOTEL_MAX_DISTANCE_ERROR,
        },
    )
    distance_to_the_center = IntegerField(
        required=False,
        min_value=0,
        max_value=200000,
        error_messages={
            "min_value": MIN_ERROR,
            "max_value": HOTEL_MAX_DISTANCE_ERROR,
        },
    )
    distance_to_the_metro = IntegerField(
        required=False,
        min_value=0,
        max_value=200000,
        error_messages={
            "min_value": MIN_ERROR,
            "max_value": HOTEL_MAX_DISTANCE_ERROR,
        },
    )
    distance_to_the_airport = IntegerField(
        required=False,
        min_value=0,
        max_value=200000,
        error_messages={
            "min_value": MIN_ERROR,
            "max_value": HOTEL_MAX_DISTANCE_ERROR,
        },
    )

    class Meta:
        model = Hotel
        fields = (
            "id",
            "name",
            "star_category",
            "place",
            "country",
            "city",
            "address",
            "distance_to_the_station",
            "distance_to_the_sea",
            "distance_to_the_center",
            "distance_to_the_metro",
            "distance_to_the_airport",
            "description",
            "check_in_time",
            "check_out_time",
            "amenities_common",
            "amenities_in_the_room",
            "amenities_sports_and_recreation",
            "amenities_for_children",
            "user_rating",
            "type_of_rest",
            "rules",
            "is_active",
            "width",
            "longitude",
        )

    def update(self, instance, validated_data):
        rules_data = validated_data.pop("hotels_rules", None)
        instance = super().update(instance, validated_data)
        if rules_data is not None:
            with transaction.atomic():
                existing_rules = {rule.name: rule for rule in instance.hotels_rules.all()}
                new_rule_names = {rule["name"] for rule in rules_data}
                # Удаляем правила, которых больше нет
                for name, rule in existing_rules.items():
                    if name not in new_rule_names:
                        rule.delete()
                # Или обновляем, или создаём новые правила
                for rule_data in rules_data:
                    rule = existing_rules.get(rule_data["name"])
                    if rule:
                        for key, value in rule_data.items():
                            setattr(rule, key, value)
                        rule.save()
                    else:
                        instance.hotels_rules.create(**rule_data)
        return instance


class HotelPhotoSerializer(ModelSerializer):
    """
    Сериализатор фотографий отеля.
    """

    photo = ImageField()

    class Meta:
        model = HotelPhoto
        fields = (
            "id",
            "photo",
            "hotel",
        )
        read_only_fields = (
            "id",
            "hotel",
        )


class HotelListWithPhotoSerializer(HotelDetailSerializer):
    """
    Промежуточная сериализация, где не нужны номера. Возвращает все поля, и фотографии отеля.
    """

    photo = HotelPhotoSerializer(
        source="hotel_photos",
        many=True,
        read_only=True,
    )

    class Meta(HotelDetailSerializer.Meta):
        fields = HotelDetailSerializer.Meta.fields + ("photo",)


class HotelListRoomAndPhotoSerializer(HotelListWithPhotoSerializer):
    """
    Полная сериализация отеля со всеми вложенными данными.
    Фотографии отеля, номера в отеле.
    Метод GET(list), GET id (retrieve).
    """

    rooms = RoomDetailSerializer(
        many=True,
        read_only=True,
    )

    class Meta(HotelListWithPhotoSerializer.Meta):
        fields = HotelListWithPhotoSerializer.Meta.fields + ("rooms",)


class HotelShortPhotoSerializer(ModelSerializer):
    photo = HotelPhotoSerializer(source="hotel_photos", many=True, read_only=True)

    class Meta:
        model = Hotel
        fields = ("photo",)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["photo"] = representation["photo"][:10]
        return representation


class HotelPopularSerializer(HotelShortPhotoSerializer):
    """
    Сериализатор для списка популярных туров.
    """

    hotels_count = IntegerField(
        min_value=0,
        required=True,
    )
    min_price_without_discount = DecimalField(
        max_digits=10,
        decimal_places=2,
        default="25000.00",
    )

    class Meta:
        model = Hotel
        fields = HotelShortPhotoSerializer.Meta.fields + (
            "country",
            "min_price_without_discount",
            "hotels_count",
        )


class HotelBaseShortSerializer(HotelShortPhotoSerializer):
    class Meta:
        model = Hotel
        fields = HotelShortPhotoSerializer.Meta.fields + (
            "id",
            "country",
            "city",
            "star_category",
            "name",
            "user_rating",
            "distance_to_the_center",
        )


class HotelShortSerializer(HotelBaseShortSerializer):
    class Meta:
        model = Hotel
        fields = HotelBaseShortSerializer.Meta.fields + (
            "distance_to_the_station",
            "distance_to_the_sea",
            "distance_to_the_metro",
            "distance_to_the_airport",
            "amenities_common",
            "width",
            "longitude",
        )


class HotelShortWithPriceSerializer(HotelShortSerializer):
    min_price_without_discount = DecimalField(
        max_digits=10,
        decimal_places=2,
        default="25000.00",
    )
    min_price_with_discount = DecimalField(
        max_digits=10,
        decimal_places=2,
        default="20000.00",
    )

    class Meta:
        model = Hotel
        fields = HotelShortSerializer.Meta.fields + (
            "min_price_without_discount",
            "min_price_with_discount",
        )


class HotelFiltersResponseSerializer(HotelShortWithPriceSerializer):
    """
    Сериализатор отеля для получения ответа из поиска.
    """

    nights = SerializerMethodField()
    guests = SerializerMethodField()

    class Meta:
        model = Hotel
        fields = HotelShortWithPriceSerializer.Meta.fields + (
            "nights",
            "guests",
        )

    @extend_schema_field(int)
    def get_nights(self, obj) -> int:
        """
        Подсчет количества ночей.
        """
        check_in = self.context.get("check_in_date")
        check_out = self.context.get("check_out_date")
        nights_default = 1
        if not check_in or not check_out:
            return nights_default
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
            return max((check_out_date - check_in_date).days, nights_default)
        except (ValueError, TypeError):
            return nights_default

    @extend_schema_field(int)
    def get_guests(self, obj) -> int:
        """
        Получение количества гостей из контекста.
        """
        return int(self.context.get("guests", 1))


class HotelFiltersRequestSerializer(Serializer):
    """
    Сериализатор для параметров расширенного поиска (все поля необязательные).
    """

    check_in_date = DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        error_messages={
            "invalid": "Некорректный формат даты. Используйте YYYY-MM-DD",
        },
    )
    check_out_date = DateField(
        required=False,
        input_formats=["%Y-%m-%d"],
        error_messages={
            "invalid": "Некорректный формат даты. Используйте YYYY-MM-DD",
        },
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
        min_value=1,
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

    class Meta:
        validators = [
            DateValidator(
                check_in_field="check_in_date",
                check_out_field="check_out_date",
            )
        ]


class HotelWithMinPriceSerializer(HotelBaseShortSerializer):
    min_price_without_discount = DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        default="5000.00",
    )
    min_price_with_discount = DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        default="4000.00",
    )

    class Meta:
        model = Hotel
        fields = HotelBaseShortSerializer.Meta.fields + (
            "min_price_without_discount",
            "min_price_with_discount",
        )


class HotelWhatAboutFullSerializer(ModelSerializer):
    hotel = HotelWithMinPriceSerializer(many=True, read_only=True)
    name_set = CharField(read_only=True)

    class Meta:
        model = HotelWhatAbout
        fields = (
            "name_set",
            "hotel",
        )
