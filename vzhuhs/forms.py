from dal import autocomplete
from django import forms

from vzhuhs.models import Vzhuh


class VzhuhForm(forms.ModelForm):
    class Meta:
        model = Vzhuh
        fields = "__all__"
        widgets = {
            "tours": autocomplete.ModelSelect2Multiple(
                url="vzhuhs:vzhuh_autocomplete_tours",
                forward=["departure_city", "arrival_city", "tours"],
                attrs={
                    "style": "width: 60%",
                },
            ),
            "hotels": autocomplete.ModelSelect2Multiple(
                url="vzhuhs:vzhuh_autocomplete_hotels",
                forward=["arrival_city", "hotels"],
                attrs={
                    "style": "width: 60%",
                },
            ),
        }
