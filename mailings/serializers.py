from rest_framework.exceptions import ValidationError
from rest_framework.serializers import BooleanField, EmailField, ModelSerializer

from mailings.models import Mailing


class MailingSerializer(ModelSerializer):
    """Сериализатор для модели Mailing."""

    email = EmailField(
        help_text="Email туриста, на который будет отправляться рассылка.",
        required=True,
        error_messages={"unique": "Этот email уже зарегистрирован."},
    )
    mailing = BooleanField(required=False)

    class Meta:
        model = Mailing
        fields = ("id", "email", "mailing")

    def validate_email(self, value):
        """Проверка, что email еще не зарегистрирован."""
        if self.instance is None and Mailing.objects.filter(email=value).exists():
            raise ValidationError(self.fields["email"].error_messages["unique"])
        return value

    def create(self, validated_data):
        validated_data.setdefault("mailing", True)
        return super().create(validated_data)

    def get_fields(self):
        fields = super().get_fields()
        if self.context.get("view").action == "partial_update":
            fields["email"].required = False
            fields["email"].read_only = True
        elif self.context.get("view").action == "update":
            fields["mailing"].required = True
        return fields
