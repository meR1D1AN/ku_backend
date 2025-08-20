from django.contrib.auth.models import BaseUserManager

from all_fixture.choices import RoleChoices
from insurances.models import Insurances


class CustomUserManager(BaseUserManager):
    """Менеджер для кастомного пользователя с email вместо username."""

    def create_user(self, email, password=None, **extra_fields):
        """Создает и возвращает обычного пользователя."""
        if not email:
            raise ValueError("Email обязателен для создания пользователя")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        role = extra_fields.get("role")

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        if role == RoleChoices.TOUR_OPERATOR:
            Insurances.objects.create(id=user)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и возвращает суперпользователя."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)
