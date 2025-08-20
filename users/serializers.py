from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from all_fixture.choices import ContactPriorityChoices, CurrencyChoices, LanguageChoices, RoleChoices
from all_fixture.validators.validators import ForbiddenWordValidator
from users.models import User

# ───── Пользователи ───────────────────────────────────────────────────────────


class BaseUserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для всех пользователей."""

    first_name = serializers.CharField(validators=[ForbiddenWordValidator()])
    last_name = serializers.CharField(validators=[ForbiddenWordValidator()])
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "phone_number", "avatar", "birth_date", "role")


class UserSerializer(BaseUserSerializer):
    """Сериализатор для обычных пользователей (туристов) с пользовательскими настройками."""

    role = serializers.CharField(default=RoleChoices.USER)
    currency = serializers.ChoiceField(
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.RUB,
        help_text="Выбор предпочитаемой валюты: RUB, EUR, USD",
    )
    language = serializers.ChoiceField(
        choices=LanguageChoices.choices,
        default=LanguageChoices.RU,
        help_text="Язык интерфейса: RU или EN",
    )
    notifications_enabled = serializers.BooleanField(
        default=True,
        help_text="Получать ли оповещения от сервиса",
    )
    preferred_contact_channel = serializers.ChoiceField(
        choices=ContactPriorityChoices.choices,
        default=ContactPriorityChoices.EMAIL,
        help_text="Приоритетный способ связи: телефон или email",
    )

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + (
            "currency",
            "language",
            "notifications_enabled",
            "preferred_contact_channel",
        )

    def validate_role(self, value):
        user = self.context["request"].user
        if not user.is_authenticated or not user.is_superuser:
            if value != RoleChoices.USER:
                raise serializers.ValidationError("Вы не можете задать роль, отличную от USER.")
        return value


class CompanyUserSerializer(BaseUserSerializer):
    """Сериализатор для Туроператоров и Отельеров."""

    company_name = serializers.CharField(required=True, validators=[ForbiddenWordValidator()])
    documents = serializers.FileField(required=False, allow_null=True)
    role = serializers.ChoiceField(
        choices=[RoleChoices.TOUR_OPERATOR, RoleChoices.HOTELIER],
        default=RoleChoices.TOUR_OPERATOR,
        help_text="Роль компании: TOUR_OPERATOR или HOTELIER",
    )

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ("company_name", "documents")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Полное обновление объекта (PUT)."""
        # Обработка загрузки документов
        if "documents" in validated_data:
            new_document = validated_data.pop("documents")
            if new_document:
                instance.documents = new_document

        # Обработка загрузки аватара
        if "avatar" in validated_data:
            new_avatar = validated_data.pop("avatar")
            if new_avatar:
                instance.avatar = new_avatar

        # Обновление остальных полей
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def validate(self, data):
        role = data.get("role", RoleChoices.TOUR_OPERATOR)
        if role == RoleChoices.USER:
            raise serializers.ValidationError("Обычный пользователь не может иметь company_name и documents.")
        if role not in [RoleChoices.TOUR_OPERATOR, RoleChoices.HOTELIER]:
            raise serializers.ValidationError("Вы можете задать только роль 'TOUR_OPERATOR' или 'HOTELIER'.")
        return data


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    email = serializers.EmailField(
        required=True,
        help_text="Email (регистр игнорируется)",
    )

    def save(self, request):
        user = super().save(request)
        # теперь User.save() приведёт email к lowercase
        user.username = user.email
        user.save(update_fields=["username"])
        return user


# ───── Аутентификация ─────────────────────────────────────────────────────────


class EmailLoginSerializer(serializers.Serializer):
    """Сериализатор для запроса кода на email."""

    email = serializers.EmailField(
        help_text="Email пользователя, на который будет отправлен код для входа.",
    )


class EmailCodeResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Сообщение об успешной отправке кода.")


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text="Email, на который отправлен код",
    )
    code = serializers.CharField(help_text="Код из письма")


class VerifyCodeResponseSerializer(serializers.Serializer):
    """Сериализатор успешного ответа с минимальной информацией."""

    role = serializers.CharField(help_text="Роль пользователя, например: USER, ADMIN")
    id = serializers.IntegerField(help_text="Уникальный идентификатор пользователя в базе данных")


class LogoutSerializer(serializers.Serializer):
    """Сериализатор для выхода из системы"""

    refresh = serializers.CharField(required=True, help_text="Refresh-токен, подлежащий аннулированию")
    access = serializers.CharField(required=False, help_text="Access-токен (не используется на сервере)")


class DeleteTokenSerializer(serializers.Serializer):
    """Сериализатор для удаления пользователя с возможностью аннулирования refresh-токена."""

    refresh = serializers.CharField(required=False, help_text="JWT refresh-токен для аннулирования (опционально).")


class LogoutSuccessResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Сообщение об успешном выходе из системы.")


# ───── Общие ошибки ───────────────────────────────────────────────────────────


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(help_text="Описание ошибки, если выход не удался.")


# ───── Проверка токена ────────────────────────────────────────────────────────


class CheckTokenSuccessResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Успешное подтверждение, что токен активен.")


class CheckTokenErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(help_text="Описание ошибки: недействительный или отсутствующий токен.")
