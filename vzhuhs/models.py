from django.contrib import admin
from django.db import models

from all_fixture.views_fixture import NULLABLE
from hotels.models import Hotel
from tours.models import Tour


class VzhuhPhoto(models.Model):
    """
    Модель фотографий Вжуха.
    """

    photos = models.ImageField(
        upload_to="vzhuhs_photos/",
    )

    class Meta:
        verbose_name = "Фото Вжуха"
        verbose_name_plural = "Фотографии Вжуха"
        ordering = ("id",)


class Vzhuh(models.Model):
    """
    Маркетинговая сущность Вжух — спецпредложения по направлениям.
    """

    departure_city = models.CharField(
        max_length=100,
        verbose_name="Город вылета",
        help_text="Введите город вылета",
    )
    arrival_city = models.CharField(
        max_length=100,
        verbose_name="Город прибытия",
        help_text="Введите город прибытия",
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Введите описание",
        **NULLABLE,
    )
    best_time_to_travel = models.TextField(
        verbose_name="Лучшее время для поездки",
        help_text="Введите лучшее время для поездки",
        **NULLABLE,
    )
    suitable_for_whom = models.TextField(
        verbose_name="Для кого подойдёт",
        help_text="Введите для кого подойдёт",
        **NULLABLE,
    )
    photos = models.ManyToManyField(
        VzhuhPhoto,
        verbose_name="Фотографии Вжуха",
        help_text="Выберите фотографии Вжуха",
        related_name="vzhuhs",
        blank=True,
    )
    tours = models.ManyToManyField(
        Tour,
        verbose_name="Вжухнутые туры",
        help_text="Выберите туры",
        related_name="vzhuhs",
        blank=True,
    )
    hotels = models.ManyToManyField(
        Hotel,
        verbose_name="Вжухнутые отели",
        help_text="Выберите отели",
        related_name="vzhuhs",
        blank=True,
    )
    description_hotel = models.TextField(
        verbose_name="Описание к отелям",
        help_text="Введите описание к отелям",
        **NULLABLE,
    )
    description_blog = models.TextField(
        verbose_name="Описание к блогу",
        help_text="Введите описание к блогу",
        **NULLABLE,
    )
    is_published = models.BooleanField(
        verbose_name="Опубликован",
        help_text="Опубликован ли Вжух",
        default=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Дата публикации",
        help_text="Дата публикации",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Дата обновления",
        help_text="Дата обновления",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Вжух"
        verbose_name_plural = "Вжухи"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["departure_city"],
            ),
        ]

    def __str__(self):
        return f"Вжух: {self.route}"

    @property
    def route(self):
        return f"{self.departure_city} → {self.arrival_city}"

    @admin.display(description="Маршрут")
    def display_route(self):
        return self.route
