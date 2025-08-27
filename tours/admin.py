from django.contrib import admin

from tours.forms import TourAdminForm
from tours.models import Tour, TourDocument


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    form = TourAdminForm
    list_display = (
        "id",
        "start_date",
        "end_date",
        "flight_to",
        "flight_from",
        "get_tour_operator_name",
        "arrival_city",
        "hotel",
        "get_rooms",
        "total_price",
        "transfer",
        "is_active",
    )
    list_filter = ("tour_operator", "hotel")
    search_fields = ("id", "start_date", "hotel__name", "tour_operator__company_name")

    @admin.display(description="Туроператор")
    def get_tour_operator_name(self, obj):
        if obj.tour_operator:
            return obj.tour_operator.company_name or obj.tour_operator.email
        return "-"

    @admin.display(description="Номера")
    def get_rooms(self, obj):
        if obj.rooms.exists():
            return ", ".join([room.category for room in obj.rooms.all()])
        return "-"


@admin.register(TourDocument)
class TourDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "tour", "document")
