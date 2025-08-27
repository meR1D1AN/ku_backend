from datetime import date

from rest_framework import serializers


class StartDateValidator:
    """
    Валидатор для проверки, что дата начала тура не в прошлом  и корректна.
    """

    def __call__(self, value):
        if isinstance(value, dict):
            start_date = value.get("start_date")
            if not start_date:
                return
            try:
                date_start_date = date.fromisoformat(start_date)
            except (ValueError, TypeError):
                if isinstance(start_date, date):
                    date_start_date = start_date
                else:
                    raise serializers.ValidationError("Некорректный формат даты. Используйте YYYY-MM-DD") from None
        else:
            date_start_date = value

        if date_start_date < date.today():
            raise serializers.ValidationError("Дата начала не может быть в прошлом")


class EndDateValidator:
    """
    Валидатор для проверки, что дата окончания тура позже даты начала.
    """

    def __call__(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")


class PriceValidator:
    """
    Валидатор для проверки, стоимости номера, она может быть пустой или же только положительной.
    """

    def __call__(self, attrs):
        price = attrs.get("total_price")
        if price is not None and price < 0:
            raise serializers.ValidationError({"total_price": "Стоимость не может быть отрицательной."})
        return attrs
