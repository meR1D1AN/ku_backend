from django.urls import include, path
from rest_framework.routers import DefaultRouter

from mailings.views import MailingViewSet

app_name = "mailings"

router = DefaultRouter()
router.register(r"mailings", MailingViewSet, basename="mailings")

urlpatterns = [
    path("", include(router.urls)),
]
