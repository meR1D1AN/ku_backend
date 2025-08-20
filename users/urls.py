from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import AuthViewSet, CompanyUserViewSet, UserViewSet

app_name = "users"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"companies", CompanyUserViewSet, basename="company_user")
router.register(r"auth", AuthViewSet, basename="auth")

urlpatterns = [
    path("", include(router.urls)),
]
