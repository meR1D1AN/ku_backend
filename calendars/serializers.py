import logging
from decimal import Decimal

from django.db import transaction
from rest_framework.fields import DecimalField
from rest_framework.serializers import ModelSerializer, ValidationError

from calendars.models import CalendarDate, CalendarPrice

logger = logging.getLogger(__name__)


class CalendarPriceSerializer(ModelSerializer):
    price = DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Цена",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        default="5000.00",
    )

    class Meta:
        model = CalendarPrice
        fields = (
            "room",
            "price",
        )


class CalendarDateSerializer(ModelSerializer):
    calendar_prices = CalendarPriceSerializer(
        many=True,
    )
    discount_amount = DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Цена",
        min_value=Decimal("0.00"),
        max_value=Decimal("99999999.00"),
        default="0.17",
    )

    class Meta:
        model = CalendarDate
        fields = (
            "id",
            "start_date",
            "end_date",
            "available_for_booking",
            "discount",
            "discount_amount",
            "calendar_prices",
        )

    def create(self, validated_data):
        calendar_prices_data = validated_data.pop("calendar_prices")
        try:
            with transaction.atomic():
                calendar_date = CalendarDate.objects.create(**validated_data)
                # Подготовка данных для bulk_create
                calendar_prices_to_create = []
                for calendar_price_data in calendar_prices_data:
                    calendar_prices_to_create.append(
                        CalendarPrice(
                            calendar_date=calendar_date,
                            room=calendar_price_data["room"],
                            price=calendar_price_data["price"],
                        )
                    )
                CalendarPrice.objects.bulk_create(calendar_prices_to_create)
        except Exception as e:
            logger.error(f"Ошибка при создании CalendarDate: {e}")
            raise ValidationError("Ошибка при создании объекта") from None

        return calendar_date

    def update(self, instance, validated_data):
        calendar_prices_data = validated_data.pop("calendar_prices")

        try:
            with transaction.atomic():
                instance.start_date = validated_data.get(
                    "start_date",
                    instance.start_date,
                )
                instance.end_date = validated_data.get("end_date", instance.end_date)
                instance.available_for_booking = validated_data.get(
                    "available_for_booking",
                    instance.available_for_booking,
                )
                instance.discount = validated_data.get("discount", instance.discount)
                instance.discount_amount = validated_data.get(
                    "discount_amount",
                    instance.discount_amount,
                )
                instance.save()
                # Удаляем старые записи
                instance.calendar_prices.all().delete()
                # Подготовка данных для bulk_create
                calendar_prices_to_create = []
                for calendar_price_data in calendar_prices_data:
                    calendar_prices_to_create.append(
                        CalendarPrice(
                            calendar_date=instance,
                            room=calendar_price_data["room"],
                            price=calendar_price_data["price"],
                        )
                    )
                CalendarPrice.objects.bulk_create(calendar_prices_to_create)
        except Exception as e:
            logger.error(f"Ошибка при обновлении CalendarDate: {e}")
            raise ValidationError("Ошибка при обновлении объекта") from None
        return instance

    def validate(self, data):
        if data["start_date"] > data["end_date"]:
            raise ValidationError("Дата окончания должна быть позже даты начала") from None
        discount = data.get("discount", False)
        discount_amount = data.get("discount_amount")
        if discount:
            if discount_amount is None:
                raise ValidationError("Поле discount_amount обязательно, если discount=True") from None
            if discount_amount <= 0:
                raise ValidationError("Поле discount_amount должно быть положительным числом") from None
        return data
