from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from all_fixture.views_fixture import DISCOUNT, NULLABLE


class CalendarDate(models.Model):
    """
    Модель для создания календаря стоимости номеров.
    """

    hotel = models.ForeignKey(
        "hotels.Hotel",
        on_delete=models.CASCADE,
        related_name="calendar_dates",
        verbose_name="Отель",
        help_text="Отель",
        **NULLABLE,
    )
    start_date = models.DateField(
        verbose_name="Начало периода стоимости категорий номеров",
        help_text="Введите дату в формате YYYY-MM-DD",
    )
    end_date = models.DateField(
        verbose_name="Конец периода стоимости категорий номеров",
        help_text="Введите дату в формате YYYY-MM-DD",
    )
    available_for_booking = models.BooleanField(
        verbose_name="Доступна для бронирования",
        help_text="Доступность категории для бронирования в этот период",
        default=True,
    )
    discount = models.BooleanField(
        verbose_name="Акция",
        help_text="Применяется ли скидка на период",
        default=False,
    )
    discount_amount = models.DecimalField(
        verbose_name="Размер скидки",
        help_text=DISCOUNT,
        max_digits=8,
        decimal_places=2,
        **NULLABLE,
        default=None,
    )

    class Meta:
        verbose_name = "Календарь стоимости номеров"
        verbose_name_plural = "Календари стоимости номеров"
        indexes = [
            models.Index(fields=["start_date", "end_date"], name="idx_calendardate_dates"),
        ]

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"


class CalendarPrice(models.Model):
    """
    Модель для создания стоимости номеров у определенныых номеров.
    """

    calendar_date = models.ForeignKey(
        CalendarDate,
        on_delete=models.CASCADE,
        related_name="calendar_prices",
        verbose_name="Календарь стоимости номеров",
        help_text="Календарь стоимости номеров",
    )
    room = models.ForeignKey(
        "rooms.Room",
        on_delete=models.CASCADE,
        related_name="calendar_prices",
        verbose_name="Номер",
        help_text="Номер",
    )
    price = models.DecimalField(
        verbose_name="Стоимость категории номеров в сутки",
        help_text="Введите стоимость категории номеров в сутки",
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("9999999.99")),
        ],
        **NULLABLE,
    )

    class Meta:
        verbose_name = "Категория номера"
        verbose_name_plural = "Категории номеров"
        indexes = [
            models.Index(fields=["room", "calendar_date"], name="idx_calendarprice_room"),
        ]

    def __str__(self):
        return f"{self.room} - {self.price}"
