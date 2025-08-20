from django.db import models


class Mailing(models.Model):
    email = models.EmailField(
        unique=True,
        verbose_name="Email для рассылки.",
        help_text="Email туриста, на который будет отправляться рассылка.",
    )
    mailing = models.BooleanField(
        default=False,
        verbose_name="Подписка на рассылку.",
        help_text="Да/Нет",
    )

    class Meta:
        verbose_name = "Рассылка писем"
        verbose_name_plural = "Рассылки писем"

    def __str__(self):
        """Строковое представление — email туриста."""
        return self.email
