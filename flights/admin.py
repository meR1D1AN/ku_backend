from django.contrib import admin

from flights.models import Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("id", "flight_number", "departure_airport", "departure_date", "airline", "price")
    list_filter = ("departure_airport", "departure_date")
    search_fields = ("departure_date",)
