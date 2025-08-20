from django.core.validators import RegexValidator
from django.db import models

from all_fixture.views_fixture import NULLABLE
from users.models import User


class PersonBase(models.Model):
    firstname = models.CharField(
        max_length=50,
        verbose_name="Имя",
    )
    lastname = models.CharField(
        max_length=50,
        verbose_name="Фамилия",
    )
    surname = models.CharField(
        max_length=50,
        verbose_name="Отчество",
        **NULLABLE,
    )
    date_born = models.DateField(
        verbose_name="Дата рождения",
        help_text="Формат: YYYY-MM-DD",
    )
    citizenship = models.CharField(
        max_length=100,
        verbose_name="Гражданство",
    )

    class Meta:
        abstract = True


class Guest(PersonBase):
    """
    Модель Гостя
    """

    russian_passport_no = models.CharField(
        verbose_name="Серия/номер российского паспорта",
        help_text="Формат: XXXX XXXXXX",
        validators=[
            RegexValidator(
                regex=r"^[0-9]{4} [0-9]{6}$",
                message="Введите серия/номер в формате: XXXX XXXXXX",
            )
        ],
        **NULLABLE,
    )

    international_passport_no = models.CharField(
        verbose_name="Серия/номер иностранного паспорта",
        help_text="Формат: XX XXXXXXXX",
        validators=[
            RegexValidator(
                regex=r"^[0-9]{2} [0-9]{7}$",
                message="Введите серия/номер в формате: XX XXXXXXXX",
            )
        ],
        **NULLABLE,
    )

    validity_international_passport = models.DateField(
        verbose_name="Срок действия иностранного паспорта",
        help_text="Формат: DD-MM-YYYY",
        **NULLABLE,
    )

    user_owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь cоздавший гостя")

    class Meta:
        verbose_name = "Гость"
        verbose_name_plural = "Гости"
        ordering = ("lastname",)

    def __str__(self):
        return f"{self.lastname} {self.firstname}"
