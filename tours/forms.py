from dal import autocomplete
from django import forms

from tours.models import Tour


class TourAdminForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = "__all__"
        widgets = {
            "hotel": autocomplete.ModelSelect2(
                url="tours:tour_autocomplete_hotels",
                attrs={"style": "width: 100%"},
            ),
            "rooms": autocomplete.ModelSelect2Multiple(
                url="tours:tour_autocomplete_rooms",
                forward=["hotel", "rooms"],
                attrs={"style": "width: 100%"},
            ),
            "type_of_meals": autocomplete.ModelSelect2Multiple(
                url="tours:tour_autocomplete_type_of_meals",
                forward=["hotel", "type_of_meals"],
                attrs={"style": "width: 100%"},
            ),
        }
