from django.urls import include, path
from rest_framework.routers import DefaultRouter

from promocodes.views import PromoCodeCheckView, PromocodesModelViewSet

router = DefaultRouter()
router.register(r"promocodes", PromocodesModelViewSet, basename="promocodes")

urlpatterns = [
    path("promocodes/check/", PromoCodeCheckView.as_view(), name="promo-code-check"),
    path("", include(router.urls)),
]
