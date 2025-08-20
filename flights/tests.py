from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from flights.models import Flight


class FlightTestCase(APITestCase):
    """
    Тесты для модели Flight
    """

    def setUp(self):
        self.flight = Flight.objects.create(
            flight_number="SW 1245",
            airline="Аэрофлот",
            departure_airport="Шереметьево",
            arrival_airport="Адлер",
            departure_date="2024-08-24",
            departure_time="08:00:00",
            arrival_date="2024-08-25",
            arrival_time="12:00:00",
            price=5000,
        )

    def test_flight_retrieve(self):
        """
        Тест проверки просмотра рейса
        """

        url = reverse("flights:flight-detail", args=(self.flight.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("flight_number"), self.flight.flight_number)

    def test_flights_list(self):
        """
        Тест проверки просмотра списка рейсов
        """

        url = reverse("flights:flight-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_flight_create_post(self):
        """
        Тест проверки создания рейса методом POST
        """

        url = reverse("flights:flight-list")
        data = {
            "flight_number": "SW 1247",
            "airline": "Аэрофлот",
            "departure_airport": "Шереметьево",
            "arrival_airport": "Сочи",
            "departure_date": "01-08-2024",
            "departure_time": "09:00:00",
            "arrival_date": "02-08-2024",
            "arrival_time": "11:00:00",
            "price": 6000,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Flight.objects.count(), 2)
        created_flight = Flight.objects.get(flight_number="SW 1247")
        self.assertEqual(created_flight.price, 6000)
        self.assertEqual(created_flight.departure_airport, "Шереметьево")
        self.assertEqual(created_flight.arrival_airport, "Сочи")

    def test_flight_update_patch(self):
        """
        Тест проверки частичного изменения рейса
        """
        url = reverse("flights:flight-detail", args=(self.flight.pk,))
        data = {
            "flight_number": "SW 1246",
            "departure_date": "22-08-2024",
            "departure_time": self.flight.departure_time,
            "arrival_date": "23-08-2024",
            "arrival_time": self.flight.arrival_time,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.flight_number, "SW 1246")

    def test_flight_update_put(self):
        """
        Тест проверки изменения рейса методом PUT
        """
        url = reverse("flights:flight-detail", args=(self.flight.pk,))
        data = {
            "flight_number": "SW 1246",
            "airline": "Аэрофлот",
            "departure_airport": "Шереметьево",
            "arrival_airport": "Сочи",
            "departure_date": "28-08-2024",
            "departure_time": "09:00:00",
            "arrival_date": "29-08-2024",
            "arrival_time": "11:00:00",
            "price": 7000,
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.flight_number, "SW 1246")
        self.assertEqual(self.flight.price, 7000)
        self.assertEqual(self.flight.arrival_airport, "Сочи")

    def test_flight_delete(self):
        """
        Тест проверки удаления рейса
        """

        url = reverse("flights:flight-detail", args=(self.flight.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Flight.objects.all().count(), 0)

    def test_forbidden_word_validator(self):
        """
        Тест проверки валидатора на наличие недопустимых слов в названии
        """
        url = reverse("flights:flight-list")
        data = {
            "flight_number": "SW 1247",
            "airline": "Аэрофлот",
            "departure_airport": "плохое_слово",
            "arrival_airport": "Сочи",
            "departure_date": "01-08-2024",
            "departure_time": "09:00:00",
            "arrival_date": "02-08-2024",
            "arrival_time": "11:00:00",
            "price": 6000,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["non_field_errors"][0], "Введено недопустимое слово")

    def test_date_validator(self):
        """
        Тест проверки валидатора даты и времени прибытия
        """
        url = reverse("flights:flight-list")
        data = {
            "flight_number": "SW 1247",
            "airline": "Аэрофлот",
            "departure_airport": "Шереметьево",
            "arrival_airport": "Сочи",
            "departure_date": "02-08-2024",
            "departure_time": "09:00:00",
            "arrival_date": "01-08-2024",
            "arrival_time": "11:00:00",
            "price": 6000,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["non_field_errors"][0], "Дата и время прилета должны быть позже даты и времени вылета."
        )
