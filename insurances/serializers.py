from rest_framework.serializers import ModelSerializer

from insurances.models import Insurances


class InsuranceSerializer(ModelSerializer):
    """
    Сериализатор для модели Insurances (Страховки)
    """

    class Meta:
        model = Insurances
        fields = (
            "id",
            "medical",
            "not_leaving",
        )
