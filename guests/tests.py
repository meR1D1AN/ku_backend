from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient

from guests.models import Guest
from users.models import User


class GuestTest(TestCase):
    """Тесты API для модели Гость"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email="test@test.ru")
        self.client.force_authenticate(user=self.user)  # Аутентифицируем пользователя

        self.guest = Guest.objects.create(
            firstname="Ivan",
            lastname="Ivanov",
            surname="Ivanovich",
            date_born="2000-12-12",
            citizenship="Россия",
            russian_passport_no="1234 567890",
            international_passport_no="12 3456789",
            validity_international_passport="2040-11-11",
            user_owner=self.user,
        )

    def test_guest_list(self):
        """Тест на получение списка гостей"""
        url = reverse("guest-list")
        response = self.client.get(url)

        # Проверка статуса
        self.assertEqual(response.status_code, HTTP_200_OK, msg=f"Ошибка: {response.content}")

        # Получаем JSON-ответ
        data = response.json()

        # Проверяем, является ли ответ списком (если нет пагинации)
        if isinstance(data, list):
            self.assertEqual(len(data), 1, msg=f"Ожидалось 1 гостя, но получили: {data}")
        elif isinstance(data, dict) and "results" in data:
            self.assertEqual(len(data["results"]), 1, msg=f"Ожидалось 1 гостя, но получили: {data['results']}")
        else:
            self.fail(f"Неожиданный формат ответа: {data}")

    def test_guest_create(self):
        """Тест на создание нового гостя"""
        url = reverse("guest-list")
        data = {
            "firstname": "Petr",
            "lastname": "Petrov",
            "surname": "Petrovich",
            "date_born": "2000-12-12",
            "citizenship": "Россия",
            "russian_passport_no": "1234 567890",
            "international_passport_no": "12 3456789",
            "validity_international_passport": "2040-11-11",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Guest.objects.count(), 2)

    def test_guest_retrieve(self):
        """Тест на получение данных о конкретном госте"""
        url = reverse("guest-detail", args=[self.guest.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["firstname"], "Ivan")

    def test_guest_put(self):
        """Тест на полное обновление данных гостя"""
        url = reverse("guest-detail", args=[self.guest.pk])
        data = {
            "firstname": "Sasha",
            "lastname": "Ivanov",
            "surname": "Ivanovich",
            "date_born": "2000-12-12",
            "citizenship": "Россия",
            "russian_passport_no": "1234 567890",
            "international_passport_no": "12 3456789",
            "validity_international_passport": "2040-11-11",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["firstname"], "Sasha")

    def test_guest_delete(self):
        """Тест на удаление гостя"""
        url = reverse("guest-detail", args=[self.guest.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(Guest.objects.count(), 0)

    def test_date_born_validator(self):
        """Тест на проверку валидности даты рождения"""
        url = reverse("guest-list")
        data = {
            "firstname": "Petr",
            "lastname": "Petrov",
            "citizenship": "Россия",
            "date_born": "2040-12-12",  # Дата в будущем
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"][0], "Дата рождения не может быть в будущем")

    def test_forbidden_word_validator(self):
        """Тест на проверку запрещенных слов"""
        url = reverse("guest-list")
        data = {
            "firstname": "Petr",
            "lastname": "Petrov",
            "citizenship": "плохое_слово",  # Запрещенное слово
            "date_born": "2000-12-12",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"][0], "Введено недопустимое слово")

    def test_validity_of_foreign_passport_validator(self):
        """Тест на проверку срока действия загранпаспорта"""
        url = reverse("guest-list")
        data = {
            "firstname": "Petr",
            "lastname": "Petrov",
            "citizenship": "Россия",
            "date_born": "2000-12-12",
            "international_passport_no": "12 3456789",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"][0], "Срок действия паспорта не указан")

        data["validity_international_passport"] = "2015-11-11"  # Паспорт просрочен
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"][0], "Срок действия паспорта истек")
