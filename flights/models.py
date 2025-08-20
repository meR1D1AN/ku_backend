from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from all_fixture.views_fixture import NULLABLE


class Flight(models.Model):
    """
    Модель для хранения информации о рейсах
    """

    flight_number = models.CharField(
        max_length=10,
        verbose_name="Номер рейса",
        help_text="Введите номер рейса в формате: AA XXXX, или AX XXX,"
        " где A-латинские буквы в верхнем регистре, X- цифры",
    )
    airline = models.CharField(
        max_length=100,
        verbose_name="Авиакомпания",
        help_text="Введите название авиакомпании",
    )
    departure_country = models.CharField(
        max_length=50,
        verbose_name="Страна вылета",
        help_text="Введите страну вылета",
        **NULLABLE,
    )
    departure_city = models.CharField(
        max_length=50,
        verbose_name="Город вылета",
        help_text="Введите город вылета",
        **NULLABLE,
    )
    departure_airport = models.CharField(
        max_length=100,
        verbose_name="Аэропорт вылета",
        help_text="Введите аэропорт вылета",
    )
    arrival_country = models.CharField(
        max_length=50,
        verbose_name="Страна прибытия",
        help_text="Введите страна прибытия",
        **NULLABLE,
    )
    arrival_city = models.CharField(
        max_length=50,
        verbose_name="Город прибытия",
        help_text="Введите город прибытия",
        **NULLABLE,
    )
    arrival_airport = models.CharField(
        max_length=100,
        verbose_name="Аэропорт прибытия",
        help_text="Введите аэропорт прибытия",
    )
    departure_date = models.DateField(
        verbose_name="Дата вылета",
        help_text="Введите дату вылета",
    )
    departure_time = models.TimeField(
        verbose_name="Время вылета",
        help_text="Введите время вылета",
    )
    arrival_date = models.DateField(
        verbose_name="Дата прибытия",
        help_text="Введите дату прибытия",
    )
    arrival_time = models.TimeField(
        verbose_name="Время прибытия",
        help_text="Введите время прибытия",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
        help_text="Введите цену билета для взрослого",
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    price_for_child = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена для ребенка",
        help_text="Введите цену билета для ребенка",
        validators=[MinValueValidator(Decimal("0.01"))],
        **NULLABLE,
    )
    service_class = models.CharField(
        max_length=100,
        verbose_name="Класс обслуживания",
        help_text="Введите класс обслуживания",
        default="Эконом",
    )
    flight_type = models.CharField(
        max_length=50,
        verbose_name="Тип рейса",
        default="Регулярный",
        help_text="Введите тип рейса",
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Багаж, ручная кладь, питание на борту, сайт авиакомпании",
        **NULLABLE,
    )

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейсы"
        ordering = ("departure_date",)

    def __str__(self):
        return (
            f"{self.flight_number}, {self.airline}, "
            f"{self.departure_city} {self.departure_airport} - "
            f"{self.arrival_city} {self.arrival_airport}"
        )
