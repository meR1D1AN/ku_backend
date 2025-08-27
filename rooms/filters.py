from datetime import datetime

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
    # Приводим к date, чтобы исключить влияние времени
    start_date = start_date.date() if isinstance(start_date, datetime) else start_date
    end_date = end_date.date() if isinstance(end_date, datetime) else end_date
    total_nights = max((end_date - start_date).days, 1)

    price_sql = """
        WITH date_series AS (
            SELECT generate_series(%s::date, (%s::date - interval '1 day'), interval '1 day')::date AS day
        ),
        calculations AS (
            SELECT 
                COUNT(DISTINCT CASE WHEN cd.available_for_booking = TRUE THEN ds.day END) AS nights,
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


class RoomFilter(FilterSet):
    date_range = DateFromToRangeFilter(
        method="filter_date_range",
        label="Диапазон дат (YYYY-MM-DD)",
    )
    number_of_adults = MultipleChoiceFilter(
        field_name="number_of_adults",
        choices=[(i, str(i)) for i in range(1, 10)],
        conjoined=False,
        label="Количество взрослых",
    )
    number_of_children = MultipleChoiceFilter(
        field_name="number_of_children",
        choices=[(i, str(i)) for i in range(1, 10)],
        conjoined=False,
        label="Количество детей",
    )
    category = MultipleChoiceFilter(
        field_name="category",
        choices=RoomCategoryChoices.choices,
        label="Категория номера",
    )

    class Meta:
        model = Room
        fields = (
            "date_range",
            "number_of_adults",
            "number_of_children",
            "category",
        )

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
