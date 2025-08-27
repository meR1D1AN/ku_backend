from django.db.models import F, OuterRef, Q, Subquery
from django_filters import (
    ChoiceFilter,
    DateFromToRangeFilter,
    FilterSet,
    MultipleChoiceFilter,
    NumberFilter,
    RangeFilter,
)

from all_fixture.choices import PlaceChoices, TypeOfHolidayChoices, TypeOfMealChoices
from all_fixture.filters.filter_fixture import filter_choices
from all_fixture.views_fixture import MAX_PRICE, MAX_RATING, MAX_STARS, MIN_PRICE, MIN_RATING, MIN_STARS
from calendars.models import CalendarPrice
from hotels.models import Hotel


class HotelFilter(FilterSet):
    """Класс фильтров для расширенного поиска отелей."""

    date_range = DateFromToRangeFilter(
        method="filter_by_dates",
        label="Диапазон дат в формате (YYYY-MM-DD)",
    )
    country = MultipleChoiceFilter(
        field_name="country",
        lookup_expr="iexact",
        label="Страна отеля",
        choices=filter_choices(model=Hotel, field="country"),
    )
    city = MultipleChoiceFilter(
        field_name="city",
        lookup_expr="iexact",
        label="Город отеля",
        choices=filter_choices(model=Hotel, field="city"),
    )
    type_of_rest = ChoiceFilter(
        field_name="type_of_rest",
        label="Тип отдыха",
        choices=TypeOfHolidayChoices.choices,
    )
    place = ChoiceFilter(
        field_name="place",
        label="Тип размещения",
        choices=PlaceChoices.choices,
    )
    type_of_meals = MultipleChoiceFilter(
        field_name="type_of_meals__name",
        label="Тип питания",
        choices=TypeOfMealChoices.choices,
    )
    number_of_adults = NumberFilter(
        field_name="rooms__number_of_adults",
        label="Количество взрослых",
    )
    number_of_children = NumberFilter(
        field_name="rooms__number_of_children",
        label="Количество детей до 17 лет",
    )
    price = RangeFilter(
        method="filter_by_price",
        label=f"Диапазон цен стоимости тура (от {MIN_PRICE} до {MAX_PRICE})",
    )
    user_rating = NumberFilter(
        field_name="user_rating",
        label=f"Пользовательская оценка (от {MIN_RATING} до {MAX_RATING})",
        lookup_expr="gte",
    )
    star_category = MultipleChoiceFilter(
        field_name="star_category",
        choices=[(i, str(i)) for i in range(MIN_STARS, MAX_STARS + 1)],
        label=f"Категория отеля (от {MIN_STARS} до {MAX_STARS})",
        lookup_expr="exact",
    )

    class Meta:
        model = Hotel
        fields = []

    def filter_by_guests(self, queryset, name, value):
        """Фильтрация по количеству гостей."""
        try:
            guests = int(value)
            return queryset.filter(
                rooms__number_of_adults__gte=guests - F("rooms__number_of_children"),
            )
        except (ValueError, TypeError):
            return queryset.none()

    def filter_by_dates(self, queryset, name, value):
        """Фильтрация по датам заезда/выезда."""
        if name == "check_in_date":
            self.check_in_date = value
        elif name == "check_out_date":
            self.check_out_date = value
        return queryset

    def filter_by_price(self, queryset, name, value):
        """Фильтрация по цене."""
        if name == "price_gte":
            self.price_gte = value
        elif name == "price_lte":
            self.price_lte = value
        return queryset

    def filter_queryset(self, queryset):
        """Основная фильтрация с учетом всех параметров."""
        queryset = super().filter_queryset(queryset)
        filters = Q(
            calendar_date__available_for_booking=True,
        )
        if hasattr(self, "check_in_date"):
            filters &= Q(
                calendar_date__start_date__lte=self.check_in_date,
            )
        if hasattr(self, "check_out_date"):
            filters &= Q(
                calendar_date__end_date__gte=self.check_out_date,
            )
        if hasattr(self, "price_gte"):
            filters &= Q(
                price__gte=self.price_gte,
            )
        if hasattr(self, "price_lte"):
            filters &= Q(
                price__lte=self.price_lte,
            )
        subquery = (
            CalendarPrice.objects.filter(room__hotel=OuterRef("pk"))
            .filter(filters)
            .order_by("price")
            .values("price")[:1]
        )
        return (
            queryset.annotate(
                min_price=Subquery(subquery),
            )
            .filter(
                min_price__isnull=False,
            )
            .order_by("min_price")
            .distinct()
        )
