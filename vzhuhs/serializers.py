from django.db.models import Min
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import DecimalField

from hotels.models import Hotel
from hotels.serializers import HotelPhotoSerializer
from tours.models import Tour
from vzhuhs.models import Vzhuh, VzhuhPhoto


def get_first_photo(self, obj, related_field="hotel_photos"):
    """
    Вспомогательная функция для получения первой фотографии
    """
    request = getattr(self, "context", {}).get("request")
    related_objects = getattr(obj, related_field, None)
    first_photo = related_objects.first() if related_objects else None
    if first_photo:
        serializer = HotelPhotoSerializer(first_photo, context={"request": request})
        photo_url = serializer.data["photo"]
        return request.build_absolute_uri(photo_url) if request else photo_url
    return None


class VzhuhPhotoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для фотографий Вжуха.
    """

    class Meta:
        model = VzhuhPhoto
        fields = ("photos",)


class VzhuhHotelShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода инфы по отелю во Вжухе.
    """

    photo = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = (
            "id",
            "photo",
            "country",
            "city",
            "star_category",
            "user_rating",
            "name",
            "distance_to_the_sea",
            "total_price",
        )

    @extend_schema_field(serializers.ImageField(allow_null=True))
    def get_photo(self, obj: Hotel):
        """
        Возвращает первую фотографию отеля, если она доступна.
        """
        return get_first_photo(self, obj, "hotel_photos")

    @extend_schema_field(
        serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            allow_null=True,
            default="25000.00",
        )
    )
    def get_total_price(self, obj: Hotel):
        """
        Вычисляет минимальную цену по связанным турам отеля, если они есть.
        """
        total_price = obj.tours.filter(total_price__isnull=False).aggregate(Min("total_price"))["total_price__min"]
        return total_price


class VzhuhTourShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода инфы по туру во Вжухе.
    """

    photo = serializers.SerializerMethodField()
    country = serializers.CharField(source="hotel.country")
    city = serializers.CharField(source="hotel.city")
    star_category = serializers.IntegerField(source="hotel.star_category")
    user_rating = serializers.FloatField(source="hotel.user_rating")
    name = serializers.CharField(source="hotel.name")
    number_of_days = serializers.SerializerMethodField()
    discount_amount = DecimalField(
        max_digits=10,
        decimal_places=2,
        default="0.17",
    )
    total_price = DecimalField(
        max_digits=10,
        decimal_places=2,
        default="150000.00",
    )

    class Meta:
        model = Tour
        fields = (
            "id",
            "photo",
            "country",
            "city",
            "star_category",
            "user_rating",
            "name",
            "discount_amount",
            "total_price",
            "start_date",
            "end_date",
            "number_of_days",
        )

    @extend_schema_field(serializers.ImageField(allow_null=True))
    def get_photo(self, obj: Tour):
        """
        Возвращает первую фотографию отеля, связанного с туром, если она доступна.
        """
        if obj.hotel:
            return get_first_photo(self, obj.hotel, "hotel_photos")
        return None

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_number_of_days(self, obj):
        """
        Вычисляет количество дней между началом и окончанием тура.
        """
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days
        return None


class VzhuhSerializer(serializers.ModelSerializer):
    """
    Сериализатор Вжуха.
    """

    tours = VzhuhTourShortSerializer(many=True)
    hotels = VzhuhHotelShortSerializer(many=True)
    photos = VzhuhPhotoSerializer(many=True)

    class Meta:
        model = Vzhuh
        fields = (
            "id",
            "departure_city",
            "arrival_city",
            "photos",
            "description",
            "best_time_to_travel",
            "suitable_for_whom",
            "tours",
            "hotels",
            "description_hotel",
            "description_blog",
            "is_published",
        )
