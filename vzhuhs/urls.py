from django.urls import include, path
from rest_framework.routers import DefaultRouter

from vzhuhs.apps import VzhuhConfig
from vzhuhs.views import VzhuhAutocompleteHotel, VzhuhAutocompleteTour, VzhuhViewSet

app_name = VzhuhConfig.name

router = DefaultRouter()
router.register("vzhuhs", VzhuhViewSet, basename="vzhuh")

urlpatterns = [
    path(
        "vzhuhs/autocomplete/hotels/",
        VzhuhAutocompleteHotel.as_view(),
        name="vzhuh_autocomplete_hotels",
    ),
    path(
        "vzhuhs/autocomplete/tours/",
        VzhuhAutocompleteTour.as_view(),
        name="vzhuh_autocomplete_tours",
    ),
    path(
        "",
        include(router.urls),
    ),
]
