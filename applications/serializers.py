from decimal import Decimal
from typing import Any

from rest_framework.exceptions import ValidationError
from rest_framework.fields import DecimalField, IntegerField
from rest_framework.serializers import CharField, ModelSerializer

from all_fixture.choices import StatusChoices
from all_fixture.validators.validators import ForbiddenWordValidator
from applications.models import (
    ApplicationHotel,
    ApplicationTour,
)
from guests.serializers import GuestSerializer
from hotels.serializers import HotelListWithPhotoSerializer
from rooms.serializers import RoomDetailSerializer
from tours.serializers import TourListSerializer


class ApplicationBaseSerializer(ModelSerializer):
    """
    Базовая сериализация для заявок.
    """

    wishes = CharField(
        validators=[ForbiddenWordValidator()],
        required=False,
        allow_blank=True,
    )
    visa_count = IntegerField(
        min_value=0,
        help_text="Количество виз",
        default=2,
    )
    med_insurance_count = IntegerField(
        min_value=0,
        help_text="Количество медицинских страховок",
        default=2,
    )
    visa_price_per_one = DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Цена визы за одного человека",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        default="2500.00",
    )
    visa_total_price = DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Итоговая цена виз за всех гостей",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        default="5000.00",
    )
    med_insurance_price_per_one = DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Цена медицинской страховки за одного человека",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        default="3000.00",
    )
    med_insurance_total_price = DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Итоговая цена медицинских страховок за всех гостей",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        default="6000.00",
    )
    cancellation_insurance_total = DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Итоговая цена страховок от невыезда для всех гостей",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        default="7000.00",
    )
    price = DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Итоговая цена заявки",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        default="150000.00",
    )
    status = CharField(
        required=False,
        allow_blank=True,
        default=StatusChoices.AWAIT_CONFIRM,
    )

    class Meta:
        fields = (
            "id",
            "email",
            "phone_number",
            "visa_count",
            "visa_price_per_one",
            "visa_total_price",
            "med_insurance_count",
            "med_insurance_price_per_one",
            "med_insurance_total_price",
            "cancellation_insurance_total",
            "wishes",
            "status",
            "price",
        )


class ApplicationTourSerializer(ApplicationBaseSerializer):
    """
    Сериализатор для создания и обновления заявок на туры.
    Методы: POST, PUT, PATCH.
    """

    class Meta(ApplicationBaseSerializer.Meta):
        model = ApplicationTour
        fields = ApplicationBaseSerializer.Meta.fields + (
            "tour",
            "quantity_guests",
        )

    def validate_tour(self, value):
        """Валидация тура"""
        if not value:
            raise ValidationError("Тур обязателен для заполнения")
        return value

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Расширенная валидация для заявок на туры"""
        data = super().validate(data)

        # Дополнительные проверки для туров
        guests_data = data.get("quantity_guests", [])
        if not guests_data:
            raise ValidationError({"quantity_guests": "Необходимо указать хотя бы одного гостя"})

        return data


class ApplicationTourListSerializer(ApplicationBaseSerializer):
    """
    Сериализатор для получения списка заявок на туры.
    Методы: GET.
    """

    tour = TourListSerializer(
        read_only=True,
    )
    quantity_guests = GuestSerializer(
        many=True,
        read_only=True,
    )

    class Meta(ApplicationBaseSerializer.Meta):
        model = ApplicationTour
        fields = ApplicationBaseSerializer.Meta.fields + (
            "tour",
            "quantity_guests",
        )
        read_only_fields = ("status", "id")


class ApplicationHotelSerializer(ApplicationBaseSerializer):
    """
    Сериализатор для создания и обновления заявок на отели.
    Методы: POST, PUT, PATCH.
    """

    class Meta(ApplicationBaseSerializer.Meta):
        model = ApplicationHotel
        fields = ApplicationBaseSerializer.Meta.fields + (
            "hotel",
            "room",
            "quantity_guests",
        )

    def validate_hotel(self, value):
        """Валидация отеля"""
        if not value:
            raise ValidationError("Отель обязателен для заполнения")
        return value

    def validate_room(self, value):
        """Валидация номера"""
        if not value:
            raise ValidationError("Номер обязателен для заполнения")
        return value

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Расширенная валидация для заявок на отели"""
        data = super().validate(data)

        # Дополнительные проверки для отелей
        guests_data = data.get("quantity_guests", [])
        if not guests_data:
            raise ValidationError({"quantity_guests": "Необходимо указать хотя бы одного гостя"})

        # Проверка соответствия номера отелю
        hotel = data.get("hotel")
        room = data.get("room")
        if hotel and room and hasattr(room, "hotel") and room.hotel != hotel:
            raise ValidationError({"room": "Выбранный номер не принадлежит указанному отелю"})

        return data


class ApplicationHotelListSerializer(ApplicationBaseSerializer):
    """
    Сериализатор для получения списка заявок на отели.
    Методы: GET.
    """

    hotel = HotelListWithPhotoSerializer(
        read_only=True,
    )
    room = RoomDetailSerializer(
        read_only=True,
    )
    quantity_guests = GuestSerializer(
        many=True,
        read_only=True,
    )

    class Meta(ApplicationBaseSerializer.Meta):
        model = ApplicationHotel
        fields = ApplicationBaseSerializer.Meta.fields + (
            "hotel",
            "room",
            "quantity_guests",
        )
        read_only_fields = ("status", "id")
