from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from all_fixture.choices import (
    ContactPriorityChoices,
    CurrencyChoices,
    LanguageChoices,
    RoleChoices,
)
from all_fixture.views_fixture import NULLABLE
from users.managers import CustomUserManager


class User(AbstractUser):
    """
    Кастомная модель пользователя для системы "Куда Угодно".

    Объединяет базовые поля пользователя, а также дополняется расширенными
    полями для Туроператоров и Отельеров. Также включает пользовательские
    настройки: предпочитаемая валюта, язык интерфейса, оповещения и канал связи.
    """

    username = None
    first_name = models.CharField(
        max_length=100,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Фамилия",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )
    phone_number = PhoneNumberField(
        region="RU",
        verbose_name="Телефон",
        help_text="Телефон в формате: +7 (XXX) XXX-XX-XX",
        unique=True,
    )
    avatar = models.ImageField(
        upload_to="users/",
        verbose_name="Аватар",
        **NULLABLE,
    )
    birth_date = models.DateField(
        verbose_name="Дата рождения",
        **NULLABLE,
    )
    company_name = models.CharField(
        max_length=150,
        verbose_name="Название компании",
        **NULLABLE,
    )
    documents = models.FileField(
        upload_to="documents/",
        verbose_name="Документы",
        **NULLABLE,
    )
    role = models.CharField(
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
        verbose_name="Роль пользователя",
    )
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.RUB,
        verbose_name="Валюта",
    )
    language = models.CharField(
        max_length=2,
        choices=LanguageChoices.choices,
        default=LanguageChoices.RU,
        verbose_name="Язык интерфейса",
    )
    notifications_enabled = models.BooleanField(
        default=True,
        verbose_name="Получать оповещения",
    )
    preferred_contact_channel = models.CharField(
        max_length=10,
        choices=ContactPriorityChoices.choices,
        default=ContactPriorityChoices.EMAIL,
        verbose_name="Приоритетный канал связи",
    )
    failed_login_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Счетчик ошибок входа",
    )
    ban_level = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Уровень бана",
    )
    ban_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Блокировка до (числа)",
    )

    # helper
    def is_banned(self) -> bool:
        """True, если действует временная блокировка."""
        return bool(self.ban_until and self.ban_until > timezone.now())

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        """Строковое представление — имя и email пользователя."""
        return f"{self.first_name} {self.last_name} ({self.email})"

    def clean(self):
        """
        Валидация полей модели пользователя в зависимости от роли:
        - Обычный пользователь не может иметь company_name и documents.
        - Туроператор и Отельер обязаны заполнить company_name и загрузить documents.
        - Только обычный пользователь может настраивать интерфейс.
        """
        super().clean()

        if self.role == RoleChoices.USER:
            if self.company_name or self.documents:
                raise ValidationError("У обычного пользователя не могут быть заполнены поля: company_name, documents.")
        elif self.role in [RoleChoices.TOUR_OPERATOR, RoleChoices.HOTELIER]:
            if not self.company_name:
                raise ValidationError("Для Туроператора и Отельера поле 'Название компании' является обязательным.")
            if not self.documents:
                raise ValidationError("Для Туроператора и Отельера необходимо загрузить документы.")

            # Проверяем, что пользователь не пытался указать туристические настройки
            if any(
                [
                    self.currency != CurrencyChoices.RUB,
                    self.language != LanguageChoices.RU,
                    self.notifications_enabled is not True,
                    self.preferred_contact_channel != ContactPriorityChoices.EMAIL,
                ]
            ):
                raise ValidationError("Настройки интерфейса доступны только обычным пользователям (туристам).")

    def save(self, *args, **kwargs):
        """
        Перед сохранением понижаем регистр email, чтобы обеспечить консистентность.
        """
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(Lower("email"), name="unique_lower_email"),
            UniqueConstraint("phone_number", name="unique_phone_number"),
        ]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("-pk",)


# ─── История попыток входа ────────────────────────────────────────────────────
class LoginAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="login_attempts",
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Когда",  # бывш. ts
    )
    success = models.BooleanField(verbose_name="Успех")
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")

    class Meta:
        verbose_name = "Попытка входа"
        verbose_name_plural = "Попытки входа"
        indexes = [models.Index(fields=["user", "-created_at"])]
        ordering = ["-created_at"]
