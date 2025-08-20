from datetime import date
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from all_fixture.views_fixture import DISCOUNT, NULLABLE
from hotels.models import Hotel
from tours.models import Tour


class Promocode(models.Model):
    photo = models.ImageField(
        upload_to="promocodes/photos/",
        verbose_name="Фотография для промокода",
        help_text="Загрузите фотографию для промокода",
        **NULLABLE,
    )
    start_date = models.DateField(
        verbose_name="Дата начала",
        help_text="Введите дату начала",
    )
    end_date = models.DateField(
        verbose_name="Дата окончания",
        help_text="Введите дату окончания",
    )
    name = models.CharField(
        max_length=50,
        verbose_name="Название промокода",
        help_text="Введите название для промокода",
    )
    code = models.CharField(
        max_length=14,
        unique=True,
        verbose_name="Промокод",
        help_text="Введите промокод (2-10 заглавных букв и 1-4 цифры). "
        "Разрешены только латинские заглавные буквы и цифры, остальное - запрещено",
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{2,10}\d{1,4}$",
                message="Промокод должен содержать от 2 до 10 заглавных латинских букв и от 1 до 4 цифр. "
                "Всё остальное - запрещено.",
            )
        ],
    )
    discount_amount = models.DecimalField(
        verbose_name="Величина скидки",
        help_text=DISCOUNT,
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("99999.99")),
        ],
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Введите описание",
        **NULLABLE,
    )
    tours = models.ManyToManyField(
        Tour,
        verbose_name="Туры",
        help_text="Туры",
        blank=True,
    )
    hotels = models.ManyToManyField(
        Hotel,
        verbose_name="Отели",
        help_text="Отели",
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Промокод активен",
    )

    def is_valid(self, check_in_date=None, check_out_date=None):
        """
        Проверяет валидность промокода.
        Если указаны даты заезда и выезда, проверяет, что промокод действует в этот период.
        Если даты не указаны, проверяет, что промокод активен на текущую дату.
        """
        if not self.is_active:
            return False

        if check_in_date and check_out_date:
            # Проверяем, что даты заезда и выезда входят в период действия промокода
            return (
                self.start_date <= check_in_date <= self.end_date
                and self.start_date <= check_out_date <= self.end_date
            )
        else:
            # Если даты не указаны, проверяем только на текущую дату
            now = date.today()
            return self.start_date <= now <= self.end_date

    def apply_discount(self, original_price):
        discount_amount = self.discount_amount
        if discount_amount < 1:
            discounted = original_price * (1 - Decimal(discount_amount))
        else:
            discounted = original_price - discount_amount
        return round(discounted, 2)

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
