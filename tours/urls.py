from django.urls import path
from rest_framework.routers import DefaultRouter

from tours.apps import ToursConfig
from tours.views import (
    TourHotView,
    TourPopularView,
    ToursAutocompleteHotel,
    ToursAutocompleteRoom,
    ToursAutocompleteTypeOfMeal,
    TourViewSet,
)

app_name = ToursConfig.name

router = DefaultRouter()
router.register("tours", TourViewSet, basename="tours")


urlpatterns = [
    path(
        "tours/hots/",
        TourHotView.as_view({"get": "list"}),
        name="tour-hots",
    ),
    path(
        "tours/populars/",
        TourPopularView.as_view({"get": "list"}),
        name="tour-populars",
    ),
    path(
        "tours/autocomplete/hotels/",
        ToursAutocompleteHotel.as_view(),
        name="tour_autocomplete_hotels",
    ),
    path(
        "tours/autocomplete/rooms/",
        ToursAutocompleteRoom.as_view(),
        name="tour_autocomplete_rooms",
    ),
    path(
        "tours/autocomplete/type-of-meals/",
        ToursAutocompleteTypeOfMeal.as_view(),
        name="tour_autocomplete_type_of_meals",
    ),
] + router.urls
