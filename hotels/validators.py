from datetime import date

from rest_framework import serializers


class DateValidator:
    """
    Валидатор для проверки, что даты посещения отеля не в прошлом и корректны.
    """

    def __init__(self, check_in_field="check_in_date", check_out_field="check_out_date"):
        self.check_in_field = check_in_field
        self.check_out_field = check_out_field

    def __call__(self, attrs):
        check_in = attrs.get(self.check_in_field)
        check_out = attrs.get(self.check_out_field)

        # Если одно поле есть, а другого нет — пропускаем валидацию
        if not check_in or not check_out:
            return

        # Проверка, что дата заезда не в прошлом
        if check_in < date.today():
            raise serializers.ValidationError({self.check_in_field: "Дата заезда не может быть в прошлом"})

        # Проверка, что дата выезда позже даты заезда
        if check_out <= check_in:
            raise serializers.ValidationError({self.check_out_field: "Дата выезда должна быть позже даты заезда"})
