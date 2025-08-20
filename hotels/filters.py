from django.db.models import F, OuterRef, Q, Subquery
from django_filters import CharFilter, DateFilter, FilterSet, NumberFilter

from calendars.models import CalendarPrice
from hotels.models import Hotel


class HotelFilter(FilterSet):
    """Класс фильтров для расширенного поиска отелей."""

    check_in_date = DateFilter(
        method="filter_by_dates",
    )
    check_out_date = DateFilter(
        method="filter_by_dates",
    )
    guests = NumberFilter(
        method="filter_by_guests",
    )
    city = CharFilter(
        field_name="city",
        lookup_expr="iexact",
    )
    type_of_rest = CharFilter(
        field_name="type_of_rest",
        lookup_expr="exact",
    )
    place = CharFilter(
        field_name="place",
        lookup_expr="exact",
    )
    price_gte = NumberFilter(
        method="filter_by_price",
    )
    price_lte = NumberFilter(
        method="filter_by_price",
    )
    user_rating = NumberFilter(
        field_name="user_rating",
        lookup_expr="gte",
    )
    star_category = NumberFilter(
        field_name="star_category",
        lookup_expr="gte",
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
