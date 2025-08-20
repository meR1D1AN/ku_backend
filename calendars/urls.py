from django.urls import path

from calendars.views import PriceCalendarViewSet

urlpatterns = [
    path(
        "<int:hotel_id>/price_calendars/",
        PriceCalendarViewSet.as_view({"get": "list", "post": "create"}),
        name="calendar-price-list",
    ),
    path(
        "<int:hotel_id>/price_calendars/<int:pk>/",
        PriceCalendarViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="calendar-price-detail",
    ),
]
