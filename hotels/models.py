from decimal import Decimal

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from all_fixture.choices import (
    PlaceChoices,
    TypeOfHolidayChoices,
    TypeOfMealChoices,
    WhatAboutChoices,
)
from all_fixture.views_fixture import NULLABLE


class Hotel(models.Model):
    """
    Класс отеля
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название отеля",
        help_text="Название отеля",
    )
    star_category = models.IntegerField(
        verbose_name="Категория отеля",
        help_text="Выберите категорию отеля (от 0 до 5)",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ],
        **NULLABLE,
    )
    place = models.CharField(
        choices=PlaceChoices.choices,
        default=PlaceChoices.HOTEL,
        max_length=100,
        verbose_name="Тип размещения",
        help_text="Тип размещения",
        **NULLABLE,
    )
    country = models.CharField(
        max_length=50,
        verbose_name="Страна",
        help_text="Страна",
        **NULLABLE,
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Город",
        help_text="Город",
        **NULLABLE,
    )
    address = models.CharField(
        max_length=100,
        verbose_name="Адрес отеля",
        help_text="Адрес отеля",
        **NULLABLE,
    )
    distance_to_the_station = models.IntegerField(
        verbose_name="Расстояние до вокзала",
        help_text="Введите расстояние до вокзала в метрах",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200000),
        ],
        **NULLABLE,
    )
    distance_to_the_sea = models.IntegerField(
        verbose_name="Расстояние до моря",
        help_text="Введите расстояние до моря в метрах",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200000),
        ],
        **NULLABLE,
    )
    distance_to_the_center = models.IntegerField(
        verbose_name="Расстояние до центра",
        help_text="Введите расстояние до центра в метрах",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200000),
        ],
        **NULLABLE,
    )
    distance_to_the_metro = models.IntegerField(
        verbose_name="Расстояние до метро",
        help_text="Введите расстояние до метро в метрах",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200000),
        ],
        **NULLABLE,
    )
    distance_to_the_airport = models.IntegerField(
        verbose_name="Расстояние до аэропорта",
        help_text="Введите расстояние до аэропорта в метрах",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(200000),
        ],
        **NULLABLE,
    )
    description = models.TextField(
        verbose_name="Описание отеля",
        help_text="Описание отеля",
        **NULLABLE,
    )
    check_in_time = models.TimeField(
        verbose_name="Время заселения",
        help_text="Время заселения",
        **NULLABLE,
    )
    check_out_time = models.TimeField(
        verbose_name="Время выезда",
        help_text="Время выезда",
        **NULLABLE,
    )
    amenities_common = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Общие",
        help_text="Общие",
        default=list,
        **NULLABLE,
    )
    amenities_in_the_room = ArrayField(
        models.CharField(max_length=100),
        verbose_name="В номере",
        help_text="В номере",
        default=list,
        **NULLABLE,
    )
    amenities_sports_and_recreation = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Спорт и отдых",
        help_text="Спорт и отдых",
        default=list,
        **NULLABLE,
    )
    amenities_for_children = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Для детей",
        help_text="Для детей",
        default=list,
        **NULLABLE,
    )
    user_rating = models.FloatField(
        verbose_name="Пользовательская оценка",
        default=0.0,
        help_text="Пользовательская оценка",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("10.0")),
        ],
        **NULLABLE,
    )
    type_of_rest = models.CharField(
        max_length=15,
        choices=TypeOfHolidayChoices.choices,
        default=TypeOfHolidayChoices.BEACH,
        verbose_name="Тип отдыха",
        help_text="Тип отдыха",
        **NULLABLE,
    )
    rules = models.ManyToManyField(
        "HotelRules",
        verbose_name="Правила в отеле",
        related_name="hotels_rules",
        help_text="Правила в отеле",
        blank=True,
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Отель работает?",
        help_text="Отель работает?",
    )
    width = models.FloatField(
        verbose_name="Широта",
        help_text="Широта (от -90 до 90)",
        default="45.554477",
        validators=[
            MinValueValidator(Decimal("-90.0")),
            MaxValueValidator(Decimal("90.0")),
        ],
        **NULLABLE,
    )
    longitude = models.FloatField(
        verbose_name="Долгота",
        help_text="Долгота (от -180 до 180)",
        default="39.833333",
        validators=[
            MinValueValidator(Decimal("-180.0")),
            MaxValueValidator(Decimal("180.0")),
        ],
        **NULLABLE,
    )

    class Meta:
        verbose_name = "Отель"
        verbose_name_plural = "Отели"
        ordering = ("name",)

    def __str__(self):
        return self.name


class HotelPhoto(models.Model):
    """
    Класс для загрузки нескольких фотографий отеля
    """

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="hotel_photos",
        verbose_name="Отель",
        help_text="Отель",
        blank=True,
    )
    photo = models.ImageField(
        upload_to="hotels/hotels/",
        verbose_name="Фотография отеля",
        help_text="Фотография отеля",
        blank=True,
    )

    class Meta:
        verbose_name = "Фотография отеля"
        verbose_name_plural = "Фотографии отеля"


class HotelRules(models.Model):
    """Правила в отеле"""

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="hotels_rules",
        verbose_name="Отель",
        help_text="Отель",
        **NULLABLE,
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Правила в отеле",
        help_text="Правила в отеле",
        **NULLABLE,
    )
    description = models.TextField(
        verbose_name="Описание правил",
        help_text="Описание правил",
        **NULLABLE,
    )

    class Meta:
        verbose_name = "Правило в отеле"
        verbose_name_plural = "Правила в отеле"
        ordering = ("name",)

    def __str__(self):
        return self.name


class TypeOfMeal(models.Model):
    """
    Модель типов питания.
    """

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="type_of_meals",
        verbose_name="Отель",
        help_text="Отель, к которому добавляются типы питания",
        **NULLABLE,
    )
    name = models.CharField(
        choices=TypeOfMealChoices.choices,
        default=TypeOfMealChoices.BREAKFAST,
        verbose_name="Выберите типа питания",
        help_text="Выберите тип питания",
        max_length=100,
    )
    price = models.DecimalField(
        verbose_name="Стоимость типа питания",
        help_text="Введите стоимость типа питания",
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("500000.00")),
        ],
    )

    class Meta:
        verbose_name = "Тип питания"
        verbose_name_plural = "Типы питания"
        constraints = [models.UniqueConstraint(fields=["hotel", "name"], name="unique_type_of_meal_in_hotel")]
        indexes = [models.Index(fields=["hotel", "name"])]

    def __str__(self):
        return f"{self.name} ({self.price})"


class HotelWhatAbout(models.Model):
    """
    Модель подборки, что насчёт...
    """

    name_set = models.CharField(
        max_length=100,
        verbose_name="Название подборки",
        help_text="Выберите название подборки",
        choices=WhatAboutChoices.choices,
        default="",
    )
    hotel = models.ManyToManyField(
        Hotel,
        verbose_name="Отель",
        help_text="Выберите отель",
        related_name="what_about_hotels",
    )

    class Meta:
        verbose_name = "Подборка что насчёт..."
        verbose_name_plural = "Подборки что на счёт..."

    def __str__(self):
        return self.name_set
