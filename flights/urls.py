from rest_framework.routers import DefaultRouter

from flights.apps import FlightsConfig
from flights.views import FlightViewSet

app_name = FlightsConfig.name

router = DefaultRouter()
router.register("", FlightViewSet)

urlpatterns = [] + router.urls
