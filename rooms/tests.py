import shutil
import tempfile

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from all_fixture.tests.fixture_hotel import get_hotel_data
from all_fixture.tests.fixture_hotel_room import get_hotel_room_data, get_hotel_room_photo_data, update_hotel_room_data
from all_fixture.tests.test_temp_image import create_test_image
from hotels.models import Hotel
from rooms.models import Room, RoomPhoto


class RoomModelTest(TestCase):
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
        self.room = Room.objects.create(**get_hotel_room_data(self.hotel))
        self.room.discount.add(self.discount)
        self.room.unavailable.add(self.unavailable)
        self.photo = RoomPhoto.objects.create(**get_hotel_room_photo_data(self.room))
        self.hotel_id = get_hotel_room_data(self.hotel.id)
        self.room_id = get_hotel_room_data(self.room.id)
        self.update_room_data = update_hotel_room_data()
        self.url_list = reverse("rooms-list", kwargs={"hotel_id": self.hotel.id})
        self.url_detail = reverse("rooms-detail", kwargs={"hotel_id": self.hotel.id, "pk": self.room.id})
        self.url_photo_list = reverse("rooms-photos-list", kwargs={"room_id": self.room.id})
        self.url_photo_detail = reverse("rooms-photo-detail", kwargs={"room_id": self.room.id, "pk": self.photo.id})

    def test_hotel_room_creation(self):
        """Тест создания номера в отеле, Модель"""
        self.assertEqual(self.room.hotel, self.hotel)
        self.assertEqual(self.room.category, "Стандарт")
        self.assertEqual(self.room.price, 6000)
        self.assertEqual(self.room.type_of_meals, "Только завтраки")
        self.assertEqual(self.room.number_of_adults, 2)
        self.assertEqual(self.room.number_of_children, 1)
        self.assertEqual(self.room.area, 50)
        self.assertEqual(self.room.quantity_rooms, 10)
        self.assertEqual(self.room.discount.count(), 1)
        self.assertIn(self.discount, self.room.discount.all())
        self.assertEqual(self.room.unavailable.count(), 1)
        self.assertIn(self.unavailable, self.room.unavailable.all())
        self.assertEqual(self.room.amenities_common, ["Общие тестовые 1", "Общие тестовые 2"])
        self.assertEqual(self.room.amenities_coffee, ["Кофе тестовый 1", "Кофе тестовый 2"])
        self.assertEqual(self.room.amenities_bathroom, ["Душ тестовый 1", "Душ тестовый 2"])
        self.assertEqual(self.room.amenities_view, ["Горы тестовые 1", "Горы тестовые 2"])

    def test_room_photo_creation(self):
        """Тест создания фотографии номера в отеле, Модель"""
        self.assertEqual(self.photo.rooms, self.room)
        self.assertTrue(self.photo.photo)
        self.assertIn(self.photo, self.room.room_photos.all())

    def test_create_room(self):
        """Тест создания номера в отеле, API"""
        response = self.client.post(self.url_list, self.hotel_id, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Room.objects.count(), 2)

    def test_list_rooms(self):
        """Тест просмотра всех номеров в отеле, API"""
        response = self.client.get(self.url_list, self.hotel_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.json()), 0)

    def test_retrieve_room(self):
        """Тест просмотра номера в отеле, API"""
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["category"], self.room.category)

    def test_update_room(self):
        """Тест обновления номера в отеле, API"""
        response = self.client.put(self.url_detail, self.update_room_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()
        self.assertEqual(self.room.category, "Люкс")
        self.assertEqual(self.room.price, 8000)
        self.assertEqual(self.room.area, 80)

    def test_delete_room(self):
        """Тест удаления номера в отеле, API"""
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Room.objects.count(), 0)

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
        self.assertEqual(RoomPhoto.objects.count(), 2)

    def test_get_hotel_photo_list(self):
        """Тест получения списка фотографий отеля, API"""
        response = self.client.get(self.url_photo_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_delete_hotel_photo(self):
        """Тест удаления фотографии отеля, API"""
        response = self.client.delete(self.url_photo_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RoomPhoto.objects.count(), 0)
