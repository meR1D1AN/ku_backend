from rest_framework.serializers import (
    CharField,
    ModelSerializer,
    SerializerMethodField,
)

from all_fixture.validators.validators import ForbiddenWordValidator
from guests.models import Guest
from guests.validators import DateBornValidator, ValidityOfForeignPassportValidator


class GuestDetailSerializer(ModelSerializer):
    """
    Сериализатор для модели Guest
    """

    firstname = CharField(validators=[ForbiddenWordValidator()])
    lastname = CharField(validators=[ForbiddenWordValidator()])
    citizenship = CharField(validators=[ForbiddenWordValidator()])

    class Meta:
        model = Guest
        fields = (
            "pk",
            "firstname",
            "lastname",
            "surname",
            "date_born",
            "citizenship",
            "russian_passport_no",
            "international_passport_no",
            "validity_international_passport",
            "user_owner",
        )
        read_only_fields = ("user_owner",)
        validators = [
            DateBornValidator(),
            ValidityOfForeignPassportValidator(),
        ]


class GuestSerializer(GuestDetailSerializer):
    """
    Сериализатор для модели Guest
    """

    user_owner = SerializerMethodField()

    class Meta(GuestDetailSerializer.Meta):
        fields = GuestDetailSerializer.Meta.fields

    def get_user_owner(self, obj: Guest) -> str:
        return f"{obj.user_owner.first_name} {obj.user_owner.last_name}"
