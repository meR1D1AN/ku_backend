from datetime import timedelta

from django.db.models import IntegerField, OuterRef, Q, Subquery
from django_filters import (
    BooleanFilter,
    ChoiceFilter,
    DateFilter,
    FilterSet,
    MultipleChoiceFilter,
    NumberFilter,
    RangeFilter,
)
from rest_framework.exceptions import ValidationError

from all_fixture.choices import PlaceChoices, TypeOfHolidayChoices
from all_fixture.filters.filter_fixture import filter_choices
from all_fixture.views_fixture import (
    MAX_ADULT_CHILDREN,
    MAX_PRICE,
    MAX_STARS,
    MIN_ADULT,
    MIN_CHILDREN,
    MIN_PRICE,
    MIN_STARS,
)
from rooms.models import Room
from tours.models import Tour
from users.models import User


class TourFilter(FilterSet):
    """Фильтры для расширенного поиска туров."""

    departure_city = ChoiceFilter(
        field_name="departure_city",
        lookup_expr="iexact",
        label="Город вылета",
        choices=filter_choices(model=Tour, field="departure_city"),
    )
    arrival_country = MultipleChoiceFilter(
        field_name="arrival_country",
        lookup_expr="iexact",
        label="Страна прибытия",
        choices=filter_choices(model=Tour, field="arrival_country"),
    )
    arrival_city = MultipleChoiceFilter(
        field_name="arrival_city",
        lookup_expr="iexact",
        label="Город прибытия",
        choices=filter_choices(model=Tour, field="arrival_city"),
    )
    publish_start_date = DateFilter(
        method="filter_publish_start_date",
        label="Дата начала публикации тура",
    )
    nights = NumberFilter(
        method="filter_by_nights",
        label="Количество ночей в туре",
    )
    type_of_rest = ChoiceFilter(
        field_name="hotel__type_of_rest",
        label="Тип отдыха",
        choices=TypeOfHolidayChoices.choices,
    )
    place = ChoiceFilter(
        field_name="hotel__place",
        label="Тип размещения",
        choices=PlaceChoices.choices,
    )
    total_price = RangeFilter(
        method="filter_by_price",
        label=f"Диапазон цен стоимости тура (от {MIN_PRICE} до {MAX_PRICE})",
    )
    user_rating = NumberFilter(
        field_name="hotel__user_rating",
        lookup_expr="gte",
        label="Рейтинг отеля",
    )
    star_category = MultipleChoiceFilter(
        field_name="hotel__star_category",
        choices=[(i, str(i)) for i in range(MIN_STARS, MAX_STARS + 1)],
        label=f"Категория отеля (от {MIN_STARS} до {MAX_STARS})",
    )
    distance_to_the_airport = NumberFilter(
        field_name="hotel__distance_to_the_airport",
        lookup_expr="gte",
        label="Расстояние до аэропорта",
    )
    tour_operator = ChoiceFilter(
        field_name="tour_operator__company_name",
        lookup_expr="exact",
        label="Туроператор",
        choices=filter_choices(model=User, field="company_name"),
    )
    number_of_adults = NumberFilter(
        method="filter_adults",
        label=f"Количество взрослых от {MIN_ADULT} человек",
    )
    number_of_children = NumberFilter(
        method="filter_childrens",
        label=f"Количество детей до 17 лет от {MIN_CHILDREN} человек",
    )
    is_active = BooleanFilter(
        method="filter_active",
        label="Тур активен?",
    )

    class Meta:
        model = Tour
        fields = []

    def _validate_price(self, value):
        """Валидация цены."""
        total_price_min = float(value.start)
        total_price_max = float(value.stop)
        if total_price_min is not None:
            if total_price_min < MIN_PRICE:
                raise ValidationError({"total_price_min": f"Минимальная цена не может быть меньше {MIN_PRICE}"})
        if total_price_max is not None:
            if total_price_max > MAX_PRICE:
                raise ValidationError({"total_price_max": f"Максимальная цена не может быть больше {MAX_PRICE}"})
        if total_price_min == total_price_max:
            raise ValidationError(
                {
                    "total_price": f"Минимальная цена {total_price_min} не может быть равна "
                    f"максимальной цене {total_price_max}"
                }
            )
        if total_price_min is not None and total_price_max is not None and total_price_min > total_price_max:
            raise ValidationError({"total_price_min": "Минимальная цена не может быть больше максимальной цены"})
        return total_price_min, total_price_max

    def filter_adults(self, queryset, name, value):
        self.number_of_adults = value
        return queryset

    def filter_childrens(self, queryset, name, value):
        self.number_of_children = value
        return queryset

    def _filter_guests(self, queryset):
        adults_min = getattr(self, "number_of_adults", None)
        children_min = getattr(self, "number_of_children", None)

        if adults_min is None:
            adults_min = MIN_ADULT
            adults_max = MAX_ADULT_CHILDREN
        else:
            adults_max = adults_min + 1

        if children_min is None:
            children_min = MIN_CHILDREN
            children_max = MAX_ADULT_CHILDREN
        else:
            children_max = children_min + 1

        rooms_subquery = Room.objects.filter(
            tours=OuterRef("pk"),
            number_of_adults__gte=adults_min,
            number_of_adults__lte=adults_max,
            number_of_children__gte=children_min,
            number_of_children__lte=children_max,
        ).order_by("number_of_adults", "number_of_children")

        queryset = queryset.annotate(
            number_of_adults=Subquery(rooms_subquery.values("number_of_adults")[:1], output_field=IntegerField()),
            number_of_children=Subquery(rooms_subquery.values("number_of_children")[:1], output_field=IntegerField()),
        ).filter(number_of_adults__isnull=False, number_of_children__isnull=False)
        return queryset

    def filter_publish_start_date(self, queryset, name, value):
        self.publish_start_date = value
        queryset = queryset.filter(publish_start_date__lte=value)
        return queryset

    def filter_by_nights(self, queryset, name, value):
        """Фильтрация по 'start_date'."""
        self.nights = int(value)
        if hasattr(self, "publish_start_date"):
            publish_start_date = self.publish_start_date
            queryset = queryset.filter(publish_end_date__gte=publish_start_date + timedelta(days=self.nights))
        return queryset

    def filter_active(self, queryset, name, value):
        self.is_active = value
        return queryset.filter(is_active=value)

    def filter_by_price(self, queryset, name, value):
        """Фильтрация по цене."""
        total_price_min, total_price_max = self._validate_price(value)

        price_filter = Q()
        if total_price_min:
            price_filter &= Q(total_price__gte=total_price_min)
        if total_price_max:
            price_filter &= Q(total_price__lte=total_price_max)
        queryset = queryset.filter(price_filter)
        return queryset

    def filter_queryset(self, queryset):
        """Основная фильтрация с обработкой ошибок валидации."""
        try:
            queryset = super().filter_queryset(queryset)
            queryset = self._filter_guests(queryset)
            if not hasattr(self, "is_active"):
                queryset = queryset.filter(is_active=True)
            return queryset.distinct().order_by("total_price")
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError({"error": str(e)}) from None
