from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from all_fixture.choices import RoomCategoryChoices
from all_fixture.views_fixture import NULLABLE


class RoomRules(models.Model):
    """
    Модель для правил в номере.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Правила в номере",
        help_text="Правила в номере",
        **NULLABLE,
    )
    option = models.BooleanField(
        verbose_name="Да/Нет",
        help_text="Да/Нет",
        default=False,
    )

    class Meta:
        verbose_name = "Правило в номере"
        verbose_name_plural = "Правила в номерах"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.option})"


class Room(models.Model):
    """
    Модель для номера в отеле.
    """

    hotel = models.ForeignKey(
        "hotels.Hotel",
        on_delete=models.CASCADE,
        related_name="rooms",
        verbose_name="Отель",
        help_text="Отель",
        **NULLABLE,
    )
    category = models.CharField(
        choices=RoomCategoryChoices.choices,
        max_length=100,
        verbose_name="Категория номера",
        help_text="Категория номера",
        **NULLABLE,
    )
    type_of_meals = models.ManyToManyField(
        "hotels.TypeOfMeal",
        related_name="rooms",
        verbose_name="Тип питания",
        help_text="Тип питания",
    )
    number_of_adults = models.IntegerField(
        verbose_name="Количество проживающих взрослых",
        help_text="Количество проживающих взрослых",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
        **NULLABLE,
    )
    number_of_children = models.IntegerField(
        verbose_name="Количество проживающих детей",
        help_text="Количество проживающих детей",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
        **NULLABLE,
    )
    double_bed = models.IntegerField(
        verbose_name="Двуспальная кровать",
        help_text="Двуспальная кровать",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(3),
        ],
        **NULLABLE,
    )
    single_bed = models.IntegerField(
        verbose_name="Односпальная кровать",
        help_text="Односпальная кровать",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ],
        **NULLABLE,
    )
    area = models.IntegerField(
        verbose_name="Площадь номера",
        help_text="Площадь номера",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(1000),
        ],
    )
    quantity_rooms = models.IntegerField(
        verbose_name="Количество номеров данного типа",
        help_text="Количество номеров данного типа",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(500),
        ],
        default=0,
    )
    amenities_common = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Общие удобства в номере",
        help_text="Общие удобства в номере, введите через запятую",
        **NULLABLE,
    )
    amenities_coffee = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Удобства кофе станции в номере",
        help_text="Удобства кофе станции в номере, введите через запятую",
        **NULLABLE,
    )
    amenities_bathroom = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Удобства ванной комнаты в номере",
        help_text="Удобства ванной комнаты в номере, введите через запятую",
        **NULLABLE,
    )
    amenities_view = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Удобства вид в номере",
        help_text="Удобства вид в номере, введите через запятую",
        **NULLABLE,
    )
    rules = models.ManyToManyField(
        RoomRules,
        related_name="rooms",
        verbose_name="Название правила",
        help_text="Введите название правила, а потом выберите его возможность использования Да/Нет",
    )
    calendar_dates = models.ManyToManyField(
        "calendars.CalendarDate",
        through="calendars.CalendarPrice",
        verbose_name="Календарь бронирования",
        help_text="Календарь бронирования",
        blank=True,
        related_name="rooms_dates",
    )

    class Meta:
        verbose_name = "Номер"
        verbose_name_plural = "Номера"
        ordering = ("hotel",)
        indexes = [
            models.Index(
                fields=["hotel", "number_of_adults", "number_of_children"],
                name="idx_rooms_hotel_guests",
            ),
        ]

    def __str__(self):
        return f"№{self.pk} - {self.category} в {self.hotel.name} №{self.hotel.pk}"


class RoomPhoto(models.Model):
    """
    Модель для фотографий в номере.
    """

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="room_photos",
        verbose_name="Номер",
        help_text="Номер",
        blank=True,
    )
    photo = models.ImageField(
        upload_to="hotels/hotels/rooms/",
        verbose_name="Фотография номера",
        help_text="Фотография номера",
        blank=True,
    )

    class Meta:
        verbose_name = "Фотография номера"
        verbose_name_plural = "Фотографии номера"
