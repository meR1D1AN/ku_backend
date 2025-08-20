from datetime import timedelta

from django.db.models import F
from django_filters import CharFilter, DateFilter, FilterSet, NumberFilter

from tours.models import Tour


class TourFilter(FilterSet):
    """Фильтры для расширенного поиска туров."""

    departure_city = CharFilter(
        field_name="departure_city",
        lookup_expr="iexact",
    )
    arrival_city = CharFilter(
        field_name="arrival_city",
        lookup_expr="iexact",
    )
    start_date = DateFilter(
        field_name="start_date",
        lookup_expr="gte",
    )
    nights = NumberFilter(
        method="filter_by_nights",
    )
    guests = NumberFilter(
        method="filter_by_guests",
    )
    city = CharFilter(
        field_name="hotel__city",
        lookup_expr="iexact",
    )
    type_of_rest = CharFilter(
        field_name="hotel__type_of_rest",
        lookup_expr="exact",
    )
    place = CharFilter(
        field_name="hotel__place",
        lookup_expr="exact",
    )
    price_gte = NumberFilter(
        field_name="total_price",
        lookup_expr="gte",
    )
    price_lte = NumberFilter(
        field_name="total_price",
        lookup_expr="lte",
    )
    user_rating = NumberFilter(
        field_name="hotel__user_rating",
        lookup_expr="gte",
    )
    star_category = NumberFilter(
        field_name="hotel__star_category",
        lookup_expr="gte",
    )
    distance_to_the_airport = NumberFilter(
        field_name="hotel__distance_to_the_airport",
        lookup_expr="lte",
    )
    tour_operator = CharFilter(
        field_name="tour_operator__company_name",
        lookup_expr="exact",
    )

    class Meta:
        model = Tour
        fields = []

    def filter_by_nights(self, queryset, name, value):
        """Фильтрация по 'start_date'."""
        try:
            nights = int(value)
            return queryset.filter(
                end_date=F("start_date") + timedelta(days=nights),
            )
        except (ValueError, TypeError):
            return queryset.none()

    def filter_by_guests(self, queryset, name, value):
        """Фильтрация по количеству гостей."""
        try:
            guests = int(value)
            return queryset.filter(
                hotel__rooms__number_of_adults__gte=guests - F("hotel__rooms__number_of_children"),
            )
        except (ValueError, TypeError):
            return queryset.none()
