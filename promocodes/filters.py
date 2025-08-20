from django_filters import CharFilter, FilterSet, NumberFilter

from promocodes.models import Promocode


class PromocodeFilterBackemd(FilterSet):
    hotels = NumberFilter(field_name="hotels__id")
    tours = NumberFilter(field_name="tours__id")
    code = CharFilter(field_name="code", lookup_expr="exact")

    class Meta:
        model = Promocode
        fields = ("hotels", "tours", "code")

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
