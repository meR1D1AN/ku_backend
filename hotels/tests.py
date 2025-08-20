import shutil
import tempfile
from decimal import Decimal

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from all_fixture.tests.fixture_hotel import (
    get_hotel_data,
    get_hotel_photo_data,
    get_hotel_rules_data,
    update_hotel_data,
)
from all_fixture.tests.test_temp_image import create_test_image
from hotels.models import Hotel, HotelPhoto, HotelRules


class HotelModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём временную директорию для MEDIA_ROOT
        cls.temp_media_root = tempfile.mkdtemp(prefix="test_media_")
        settings.MEDIA_ROOT = cls.temp_media_root

    @classmethod
    def tearDownClass(cls):
        # Удаляем временную директорию после завершения всех тестов
        shutil.rmtree(cls.temp_media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()
        self.hotel = Hotel.objects.create(**get_hotel_data())
        self.photo = HotelPhoto.objects.create(**get_hotel_photo_data(self.hotel))
        self.rule = HotelRules.objects.create(**get_hotel_rules_data(self.hotel))
        self.update_hotel_data = update_hotel_data()
        self.url_list = reverse("hotels-list")
        self.url_detail = reverse("hotels-detail", args=[self.hotel.id])
        self.url_photo_list = reverse("hotels-photos-list", args=[self.hotel.id])
        self.url_photo_detail = reverse("hotels-photos-detail", args=[self.hotel.id, self.photo.id])

    def test_hotel_creation(self):
        """Тест создания отеля, Модель"""
        self.assertEqual(self.hotel.name, "Тестовый отель")
        self.assertEqual(self.hotel.star_category, 5)
        self.assertEqual(self.hotel.place, "Отель")
        self.assertEqual(self.hotel.country, "Россия")
        self.assertEqual(self.hotel.city, "Москва")
        self.assertEqual(self.hotel.address, "ул. Пушкина, д. 1")
        self.assertEqual(self.hotel.distance_to_the_station, 3500)
        self.assertEqual(self.hotel.distance_to_the_sea, 20000)
        self.assertEqual(self.hotel.distance_to_the_center, 2000)
        self.assertEqual(self.hotel.distance_to_the_metro, 1500)
        self.assertEqual(self.hotel.distance_to_the_airport, 3000)
        self.assertEqual(self.hotel.description, "Тестовое описание")
        self.assertEqual(self.hotel.check_in_time.strftime("%H:%M:%S"), "14:00:00")
        self.assertEqual(self.hotel.check_out_time.strftime("%H:%M:%S"), "12:00:00")
        self.assertEqual(self.hotel.amenities_common, ["Wi-Fi", "Парковка"])
        self.assertEqual(self.hotel.amenities_in_the_room, ["ТВ", "Мини-бар"])
        self.assertEqual(self.hotel.amenities_sports_and_recreation, ["Бассейн", "Тренажёрный зал"])
        self.assertEqual(self.hotel.amenities_for_children, ["Детская площадка"])
        self.assertEqual(self.hotel.type_of_meals_ultra_all_inclusive, 5000)
        self.assertEqual(self.hotel.type_of_meals_all_inclusive, 4000)
        self.assertEqual(self.hotel.type_of_meals_full_board, 3000)
        self.assertEqual(self.hotel.type_of_meals_half_board, 2000)
        self.assertEqual(self.hotel.type_of_meals_only_breakfast, 1000)
        self.assertEqual(self.hotel.user_rating, 8.5)
        self.assertEqual(self.hotel.type_of_rest, "Пляжный")
        self.assertEqual(self.hotel.is_active, True)
        self.assertEqual(self.hotel.room_categories, ["Стандарт", "Делюкс"])

    def test_hotel_photo_creation(self):
        """Тест создания фотографии отеля, Модель"""
        self.assertEqual(self.photo.hotel, self.hotel)
        self.assertIsNotNone(self.photo.photo)
        self.assertTrue(
            self.photo.photo.name.startswith("hotels/hotels/"),
            "Фотография не загружена",
        )

    def test_hotel_rules_creation(self):
        """Тест создания правил, Модель"""
        self.assertEqual(self.rule.hotel, self.hotel)
        self.assertEqual(self.rule.name, "Тестовое название правила")
        self.assertEqual(self.rule.description, "Тестовое описание правила")

    def test_create_hotel(self):
        """Тест создания отеля, API"""
        response = self.client.post(self.url_list, get_hotel_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Hotel.objects.count(), 2)

    def test_get_hotel_list(self):
        """Тест получения списка отелей, API"""
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_hotel_detail(self):
        """Тест получения деталей отеля, API"""
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], self.hotel.name)

    def test_update_hotel(self):
        """Тест обновления отеля, API"""
        response = self.client.put(self.url_detail, self.update_hotel_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.hotel.refresh_from_db()
        self.assertEqual(self.hotel.name, "Обновлённый тестовый отель")
        self.assertEqual(self.hotel.star_category, 4)
        self.assertEqual(self.hotel.room_categories, ["Стандарт", "Люкс"])
        self.assertEqual(self.hotel.user_rating, Decimal("8.9"))

    def test_delete_hotel(self):
        """Тест удаления отеля, API"""
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Hotel.objects.count(), 0)

    def test_create_hotel_photo(self):
        """Тест создания фотографии отеля, API"""
        # Создаём временное изображение, так как если использовать self.photo_data получаю ошибку:
        # {'photo': [ErrorDetail(string='Отправленный файл пуст.', code='empty')]}
        test_image = create_test_image()
        photo_data = {
            "hotel": self.hotel.id,
            "photo": test_image,
        }
        response = self.client.post(self.url_photo_list, photo_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HotelPhoto.objects.count(), 2)

    def test_get_hotel_photo_list(self):
        """Тест получения списка фотографий отеля, API"""
        response = self.client.get(self.url_photo_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_delete_hotel_photo(self):
        """Тест удаления фотографии отеля, API"""
        response = self.client.delete(self.url_photo_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(HotelPhoto.objects.count(), 0)
