from django import forms
from django.db.models import Prefetch
from django.db.models.expressions import RawSQL
from django_filters import (
    DateFromToRangeFilter,
    FilterSet,
    MultipleChoiceFilter,
)
from rest_framework.exceptions import ValidationError

from all_fixture.choices import RoomCategoryChoices
from calendars.models import CalendarDate
from rooms.models import Room


def annotate_with_prices(queryset, start_date, end_date):
    # Рассчитываем общее количество ночей в запрашиваемом диапазоне
    total_nights = (end_date - start_date).days

    price_sql = """
        WITH date_series AS (
            SELECT generate_series(%s::date, (%s::date - interval '1 day'), interval '1 day')::date AS day
        ),
        calculations AS (
            SELECT 
                COUNT(DISTINCT CASE 
                    WHEN cd.available_for_booking = TRUE THEN ds.day 
                END) AS nights,
                COALESCE(SUM(cp.price), 0) AS total_price_without_discount,
                COALESCE(
                    SUM(
                        CASE 
                            WHEN cd.discount = TRUE AND cd.discount_amount IS NOT NULL THEN 
                                CASE 
                                    WHEN cd.discount_amount <= 1.0 THEN GREATEST(cp.price * (1 - cd.discount_amount), 0)
                                    ELSE GREATEST(cp.price - cd.discount_amount, 0)
                                END
                            ELSE cp.price
                        END
                    ),
                    0
                ) AS total_price_with_discount
            FROM date_series ds
            JOIN calendars_calendardate cd ON ds.day BETWEEN cd.start_date AND cd.end_date
            JOIN calendars_calendarprice cp ON cp.calendar_date_id = cd.id
            WHERE cp.room_id = rooms_room.id
        )
        SELECT 
            total_price_without_discount AS price_without_discount,
            total_price_with_discount AS price_with_discount,
            nights AS available_count
        FROM calculations
    """

    params = (start_date, end_date)
    queryset = queryset.annotate(
        total_price_without_discount=RawSQL(
            f"SELECT price_without_discount FROM ({price_sql}) AS subquery",
            params,
        ),
        total_price_with_discount=RawSQL(
            f"SELECT price_with_discount FROM ({price_sql}) AS subquery",
            params,
        ),
        nights=RawSQL(
            f"SELECT available_count FROM ({price_sql}) AS subquery",
            params,
        ),
    )
    # Фильтруем по полному покрытию
    queryset = queryset.filter(nights=total_nights)
    return queryset


class IntMultiChoiceFilter(MultipleChoiceFilter):
    """
    - value  '00' … '10' → Swagger показывает в правильном порядке
    - label  тоже '00' … '10' (можно оставить как есть)
    - coerce=int позволяет присылать и `4`, и `04`
    """

    field_class = forms.TypedMultipleChoiceField

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("coerce", int)

        # генерируем одинаковые value/label с ведущим нулём
        kwargs["choices"] = [(f"{i:02}", f"{i:02}") for i in range(0, 11)]

        super().__init__(*args, **kwargs)


class RoomFilter(FilterSet):
    date_range = DateFromToRangeFilter(
        method="filter_date_range",
        label="Диапазон дат (YYYY-MM-DD)",
    )
    number_of_adults = IntMultiChoiceFilter(
        field_name="number_of_adults",
        label="Количество взрослых",
    )

    number_of_children = IntMultiChoiceFilter(
        field_name="number_of_children",
        label="Количество детей",
    )
    category = MultipleChoiceFilter(
        field_name="category",
        choices=RoomCategoryChoices.choices,
        label="Категория номера",
    )

    # 👉 новый фильтр: общее число гостей (взрослые + дети) : если понадобиться фильтровать по N гостей
    """
        total_guests = NumberFilter(
        method="filter_total_guests",
        label="Всего гостей",
    )
    """

    class Meta:
        model = Room
        fields = (
            "date_range",
            "number_of_adults",
            "number_of_children",
            "category",
            # "total_guests", #  👉 если понадобиться фильтровать по N гостей
        )

    #  👉 если понадобиться фильтровать по N гостей
    # В этом случае не забыть добавить импорты django.db.models > F, django_filters > NumberFilter
    '''
        def filter_total_guests(self, queryset, name, value):
        """
        value — это число, которое пришло из query-param (?total_guests=3).
        Фильтруем номера, где number_of_adults + number_of_children == value
        """
        return (
            queryset
            .annotate(total_guests=F("number_of_adults") + F("number_of_children"))
            .filter(total_guests=value)
        )
    '''

    def filter_date_range(self, queryset, name, value):
        start_date = value.start
        end_date = value.stop
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Дата начала должна быть раньше даты окончания")

            # Используем объединенную аннотацию
            queryset = annotate_with_prices(queryset, start_date, end_date)

            # Добавляем prefetch_related для отображения дат
            prefetch_queryset = CalendarDate.objects.filter(
                start_date__lte=end_date,
                end_date__gte=start_date,
                available_for_booking=True,
            )
            queryset = queryset.prefetch_related(Prefetch("calendar_dates", queryset=prefetch_queryset))

            return queryset
        return queryset
