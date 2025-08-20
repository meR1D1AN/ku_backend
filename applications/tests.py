from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APIClient

from applications.models import ApplicationTour, Guest
from tours.models import Tour
from users.models import User


class ApplicationTest(TestCase):
    """
    Тесты для модели Application
    """

    def setUp(self):
        """
        Экземпляр модели Заявка
        """
        self.user = User.objects.create(email="test@test.ru", password="testpassword")
        self.client = APIClient()
        self.tour = Tour.objects.create(start_date="2028-08-24", end_date="2028-08-25", departure_city="Москва")
        self.guest = Guest.objects.create(
            firstname="Иван", lastname="Иванов", date_born="1999-09-09", citizenship="Россия", user_owner=self.user
        )
        self.application = ApplicationTour.objects.create(
            tour=self.tour,
            email="test@test.ru",
            phone_number="+7(999)999-99-99",
            visa=False,
            med_insurance=True,
            cancellation_insurance=True,
            wishes="test wishes",
            status="Подтвержден",
            user_owner=self.user,
        )
        self.application.quantity_guests.add(self.guest)
        self.client.force_authenticate(user=self.user)

    def test_application(self):
        """
        Тест модели Заявки
        """

        self.assertEqual(self.application.tour, self.tour)
        self.assertEqual(self.application.email, "test@test.ru")
        self.assertEqual(self.application.phone_number, "+7(999)999-99-99")
        self.assertEqual(self.application.visa, False)
        self.assertEqual(self.application.med_insurance, True)
        self.assertEqual(self.application.cancellation_insurance, True)
        self.assertEqual(self.application.wishes, "test wishes")
        self.assertEqual(self.application.status, "Подтвержден")
        self.assertEqual(self.application.user_owner, self.user)

    def test_application_list(self):
        """Тест на вывод списка заявок"""

        url = reverse("applications:application-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("results" in response.data)

    def test_applications_create(self):
        """Тест создания заявки"""

        self.client.login(email="test@test.ru", password="testpassword")

        url = reverse("applications:application-list")
        data = {
            "tour": self.tour.id,
            "email": "user@example.com",
            "phone_number": "+79999999999",
            "quantity_guests": [self.guest.id],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ApplicationTour.objects.count(), 2)

    def test_forbidden_word_validator(self):
        """Тест на проверку запрещенных слов"""
        url = reverse("applications:application-list")
        data = {
            "tour": self.tour.id,
            "email": "user@example.com",
            "phone_number": "+79999999999",
            "quantity_guests": [self.guest.id],
            "wishes": "плохое_слово",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"][0], "Введено недопустимое слово")

    def test_application_retrieve(self):
        """Тест на вывод конкретной заявки"""

        url = reverse("applications:application-detail", args=(self.application.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["email"], "test@test.ru")

    def test_applications_put(self):
        """Тест на обновление заявки"""

        url = reverse("applications:application-detail", args=(self.application.pk,))
        data = {
            "pk": 6,
            "tour": self.tour.pk,
            "email": "test1@test.ru",
            "phone_number": "+79999999988",
            "visa": 1,
            "med_insurance": False,
            "cancellation_insurance": False,
            "wishes": "test wishes new",
            "status": "Подтвержден",
            "user_owner": self.user.pk,
            "quantity_guests": [self.guest.pk],
        }

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["wishes"], "test wishes new")

    def test_application_patch(self):
        """Тест на частичное обновление заявки"""

        url = reverse("applications:application-detail", args=(self.application.pk,))
        data = {
            "email": "test2@test.ru",
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()["email"], "test2@test.ru")

    def test_applications_delete(self):
        """Удаление заявки"""

        url = reverse("applications:application-detail", args=(self.application.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ApplicationTour.objects.count(), 0)
