from django.db import models

from all_fixture.validators.models import MIN_0_MAX_9KK, MIN_0_MAX_99K
from all_fixture.views_fixture import DISCOUNT, NULLABLE
from flights.models import Flight
from hotels.models import Hotel, TypeOfMeal
from rooms.models import Room
from users.models import User


class Tour(models.Model):
    """
    Модель для хранения информации о турах.
    """

    start_date = models.DateField(
        verbose_name="Дата начала тура",
        help_text="Введите дату начала тура",
    )
    end_date = models.DateField(
        verbose_name="Дата окончания тура",
        help_text="Введите дату окончания тура",
    )
    flight_to = models.ForeignKey(
        Flight,
        on_delete=models.SET_NULL,
        verbose_name="Рейс отправления",
        related_name="tours",
        help_text="Введите ID рейса отправления",
        **NULLABLE,
    )
    flight_from = models.ForeignKey(
        Flight,
        on_delete=models.SET_NULL,
        verbose_name="Рейс возвращения",
        help_text="Введите ID рейса возвращения",
        **NULLABLE,
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
        help_text="Введите город вылеты",
        **NULLABLE,
    )
    arrival_country = models.CharField(
        max_length=50,
        verbose_name="Страна прибытия",
        help_text="Страну прибытия",
        **NULLABLE,
    )
    arrival_city = models.CharField(
        max_length=50,
        verbose_name="Город прибытия",
        help_text="Город прибытия",
        **NULLABLE,
    )
    tour_operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name="Туроператор",
        related_name="tours",
        help_text="Введите ID туроператора",
        **NULLABLE,
    )
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.SET_NULL,
        verbose_name="Отель",
        related_name="tours",
        help_text="Введите ID отеля",
        **NULLABLE,
    )
    rooms = models.ManyToManyField(
        Room,
        verbose_name="Номер",
        related_name="tours",
        help_text="Введите ID номера",
        blank=True,
    )
    type_of_meals = models.ManyToManyField(
        TypeOfMeal,
        verbose_name="Типы питания",
        related_name="tours",
        help_text="Выберите типы питания, который есть в этом отеле для этого тура",
        blank=True,
    )
    transfer = models.BooleanField(
        verbose_name="Использовать трансфер отельера",
        default=False,
        help_text="Отметьте использовать трансфер отельера",
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Итоговая стоимость тура",
        help_text="Введите итоговую стоимость тура",
        validators=MIN_0_MAX_9KK,
        **NULLABLE,
    )
    discount_amount = models.DecimalField(
        verbose_name="Размер скидки на тур",
        help_text=DISCOUNT,
        max_digits=10,
        decimal_places=2,
        validators=MIN_0_MAX_99K,
        **NULLABLE,
    )
    discount_start_date = models.DateField(
        verbose_name="Дата начала скидки",
        help_text="Введите дату начала скидки",
        **NULLABLE,
    )
    discount_end_date = models.DateField(
        verbose_name="Дата окончания скидки",
        help_text="Введите дату окончания скидки",
        **NULLABLE,
    )
    markup_amount = models.DecimalField(
        verbose_name="Наценка на тур",
        help_text=DISCOUNT,
        max_digits=10,
        decimal_places=2,
        validators=MIN_0_MAX_99K,
        **NULLABLE,
    )
    publish_start_date = models.DateField(
        verbose_name="Дата публикации тура",
        help_text="Введите дату публикации тура",
        **NULLABLE,
    )
    publish_end_date = models.DateField(
        verbose_name="Дата снятия тура с публикации",
        help_text="Введите дату снятия тура с публикации",
        **NULLABLE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        **NULLABLE,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата последнего изменения",
        **NULLABLE,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Тур активен?",
        help_text="Тур активен?",
    )

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        ordering = ("start_date",)

    def __str__(self):
        hotel_name = self.hotel.name if self.hotel else "неизвестный отель"
        if self.tour_operator:
            if self.tour_operator.company_name:
                return f"Тур от {self.tour_operator.company_name} в {hotel_name}"
            return f"Тур от {self.tour_operator.email} в {hotel_name}"
        return f"Тур в {hotel_name}"


class TourDocument(models.Model):
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="tour_documents",
        verbose_name="Документы по туру",
        help_text="Документы по туру",
        blank=True,
    )
    document = models.FileField(
        upload_to="tour/documents",
        verbose_name="Документы",
        help_text="Загрузите документы по туру",
        **NULLABLE,
    )

    class Meta:
        verbose_name = "Документы по туру"
        verbose_name_plural = "Документы по турам"

    def __str__(self):
        return f"Документы по туру {self.tour}"
