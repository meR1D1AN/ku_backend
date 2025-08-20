from rest_framework.fields import DecimalField, TimeField
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from all_fixture.validators.validators import DateValidator
from flights.models import Flight


class FlightSerializer(ModelSerializer):
    departure_time = TimeField(default="13:00")
    arrival_time = TimeField(default="15:00")
    price = DecimalField(
        max_digits=10,
        decimal_places=2,
        default="8000.00",
    )
    price_for_child = DecimalField(
        max_digits=10,
        decimal_places=2,
        default="4000.00",
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "flight_number",
            "airline",
            "departure_country",
            "departure_city",
            "departure_airport",
            "arrival_country",
            "arrival_city",
            "arrival_airport",
            "departure_date",
            "departure_time",
            "arrival_date",
            "arrival_time",
            "price",
            "price_for_child",
            "service_class",
            "flight_type",
            "description",
        )

        validators = [
            UniqueTogetherValidator(
                fields=["flight_number", "departure_date"],
                queryset=Flight.objects.all(),  # Валидатор для проверки уникальности рейса в конкретную дату
            ),
            DateValidator(),
        ]
