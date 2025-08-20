from django.db import models

from all_fixture.choices import MedicalInsuranceChoices, NotLeavingInsuranceChoices
from all_fixture.views_fixture import NULLABLE


class Insurances(models.Model):
    id = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="insurance",
        verbose_name="Пользователь",
    )
    medical = models.CharField(
        choices=MedicalInsuranceChoices.choices,
        default="",
        verbose_name="Медицинская страховка",
        help_text="Медицинская страховка",
        **NULLABLE,
    )
    not_leaving = models.CharField(
        choices=NotLeavingInsuranceChoices.choices,
        default="",
        verbose_name="Страховка от невыезда",
        help_text="Страховка от невыезда",
        **NULLABLE,
    )

    class Meta:
        verbose_name = "Страховка"
        verbose_name_plural = "Страховки"

    def __str__(self):
        return f"{self.medical if self.medical else ''} {self.not_leaving if self.not_leaving else ''}"
