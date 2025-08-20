from datetime import date

from rest_framework.exceptions import ValidationError


class DateBornValidator:
    """
    Проверка, что дата рождения не в будущем.
    """

    def __call__(self, value):
        if value.get("date_born") and value.get("date_born") > date.today():
            raise ValidationError("Дата рождения не может быть в будущем")


class ValidityOfForeignPassportValidator:
    """
    Проверка наличия корректного срока у иностранного паспорта.
    """

    def __call__(self, value):
        international_passport_no = value.get("international_passport_no")
        validity_international_passport = value.get("validity_international_passport")
        if international_passport_no and not validity_international_passport:
            raise ValidationError("Срок действия паспорта не указан")
        if validity_international_passport is not None and validity_international_passport < date.today():
            raise ValidationError("Срок действия паспорта истек")
