from datetime import datetime
from pathlib import Path

from rest_framework.exceptions import ValidationError


class ForbiddenWordValidator:
    """
    Валидатор на наличие недопустимых слов в названии.
    """

    def __init__(self):
        self.forbidden_words = self.load_forbidden_words()

    def load_forbidden_words(self):
        """
        Загружает запрещенные слова из файла forbidden_words.txt.
        """
        base_dir = Path(__file__).parent
        file_path = base_dir / "forbidden_words.txt"
        try:
            with open(file_path, encoding="utf-8") as file:
                return [word.strip() for word in file.read().splitlines()]
        except FileNotFoundError:
            raise FileNotFoundError("Файл forbidden_words.txt не был найден.") from None

    def __call__(self, value):
        """
        Проверяет, содержит ли значение запрещённые слова.
        """
        if isinstance(value, str) and any(word in value.lower() for word in self.forbidden_words):
            raise ValidationError("Введено недопустимое слово")
        return value


class DateValidator:
    """
    Валидатор для проверки, что дата и время прибытия позже даты и времени отправления.
    """

    def __call__(self, value):
        departure_date_field = value.get("departure_date")
        departure_time_field = value.get("departure_time")
        arrival_date_field = value.get("arrival_date")
        arrival_time_field = value.get("arrival_time")

        departure_datetime = datetime.combine(departure_date_field, departure_time_field)
        arrival_datetime = datetime.combine(arrival_date_field, arrival_time_field)
        if arrival_datetime <= departure_datetime:
            raise ValidationError("Дата и время прилета должны быть позже даты и времени вылета.")
