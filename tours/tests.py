from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tours.models import Tour


class TourTestCase(APITestCase):
    """
    Тесты для модели Tour.
    """

    def setUp(self):
        self.tour = Tour.objects.create(start_date="2028-08-24", end_date="2028-08-25", departure_city="Москва")

    def test_tour_retrieve(self):
        """
        Тест проверки просмотра тура
        """
        url = reverse("tours:tour-detail", args=(self.tour.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("start_date"), "24-08-2028")

    def test_tours_list(self):
        """
        Тест проверки просмотра списка туров
        """
        url = reverse("tours:tour-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_tour_create(self):
        """
        Тест проверки создания тура методом POST
        """
        url = reverse("tours:tour-list")
        data = {"start_date": "24-08-2028", "end_date": "25-08-2028", "departure_city": "Казань"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tour.objects.count(), 2)

    def test_tour_update_put(self):
        """
        Тест проверки изменения тура методом PUT
        """
        url = reverse("tours:tour-detail", args=(self.tour.pk,))
        data = {
            "start_date": "25-08-2028",
            "end_date": "26-08-2028",
            "departure_city": "Санкт-Петербург",
            "number_of_adults": 3,
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tour.refresh_from_db()
        self.assertEqual(self.tour.start_date, date(2028, 8, 25))
        self.assertEqual(self.tour.end_date, date(2028, 8, 26))
        self.assertEqual(self.tour.departure_city, "Санкт-Петербург")
        self.assertEqual(self.tour.number_of_adults, 3)

    def test_tour_update_patch(self):
        """
        Тест проверки изменения тура
        """
        url = reverse("tours:tour-detail", args=(self.tour.pk,))
        data = {"start_date": "25-08-2028", "end_date": "26-08-2028", "number_of_adults": 5}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tour.refresh_from_db()
        self.assertEqual(self.tour.number_of_adults, 5)

    def test_tour_delete(self):
        """
        Тест проверки удаления тура
        """
        url = reverse("tours:tour-detail", args=(self.tour.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tour.objects.all().count(), 0)

    def test_start_date(self):
        """
        Тест проверки, что дата начала тура не может быть в прошлом.
        """
        url = reverse("tours:tour-list")
        past_date = (date.today() - timedelta(days=1)).strftime("%d-%m-%Y")
        data = {"start_date": past_date, "end_date": "25-08-2028", "departure_city": "Москва"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Дата начала тура не может быть в прошлом.")

    def test_end_date(self):
        """
        Тест проверки, что дата окончания тура не может быть раньше даты начала.
        """
        url = reverse("tours:tour-list")
        data = {"start_date": "25-08-2028", "end_date": "23-08-2028", "departure_city": "Москва"}

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Дата окончания тура не может быть раньше даты начала.")
