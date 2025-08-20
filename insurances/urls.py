from django.urls import path

from insurances.apps import InsuranceConfig
from insurances.views import InsurancesView

app_name = InsuranceConfig.name

urlpatterns = [
    path(
        "<int:pk>/",
        InsurancesView.as_view({"get": "retrieve", "put": "update"}),
        name="insurances",
    )
]
