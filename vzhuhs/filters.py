from django_filters import CharFilter, FilterSet
from rest_framework.exceptions import ValidationError

from .models import Vzhuh


class VzhuhFilter(FilterSet):
    departure_city = CharFilter(method="filter_departure_city")

    class Meta:
        model = Vzhuh
        fields = ["departure_city"]

    def filter_departure_city(self, queryset, name, value):
        if value:
            # Проверяем, что введенный город существует в базе данных
            if not queryset.filter(departure_city__iexact=value).exists():
                raise ValidationError(f"Город вылета '{value}' не найден.")
            return queryset.filter(departure_city__iexact=value)
        return queryset
