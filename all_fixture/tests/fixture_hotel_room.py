from django.utils import timezone

from all_fixture.tests.test_temp_image import create_test_image


def get_hotel_room_data(hotel):
    """Фикстура номера в отеле"""
    return {
        "hotel": hotel,
        "category": "Стандарт",
        "price": 6000,
        "type_of_meals": "Только завтраки",
        "number_of_adults": 2,
        "number_of_children": 1,
        "single_bed": 1,
        "double_bed": 1,
        "area": 50,
        "quantity_rooms": 10,
        "amenities_common": ["Общие тестовые 1", "Общие тестовые 2"],
        "amenities_coffee": ["Кофе тестовый 1", "Кофе тестовый 2"],
        "amenities_bathroom": ["Душ тестовый 1", "Душ тестовый 2"],
        "amenities_view": ["Горы тестовые 1", "Горы тестовые 2"],
    }


def update_hotel_room_data():
    """Фикстура обновленных данных номера в отеле"""
    return {
        "category": "Люкс",
        "price": 8000,
        "type_of_meals": "Всё включено",
        "number_of_adults": 2,
        "number_of_children": 0,
        "single_bed": 1,
        "double_bed": 0,
        "area": 80,
        "quantity_rooms": 2,
        "amenities_common": ["Общие тестовые 3", "Общие тестовые 4"],
        "amenities_coffee": ["Кофе тестовый 3", "Кофе тестовый 4"],
        "amenities_bathroom": ["Душ тестовый 3", "Душ тестовый 4"],
        "amenities_view": ["Горы тестовые 3", "Горы тестовые 4"],
    }


def get_hotel_room_discount_data():
    """Фикстура данных скидки номера отеля"""
    return {
        "name": "Сезонная скидка",
        "size": 15,
        "start_date": timezone.now().date(),
        "end_date": timezone.now().date() + timezone.timedelta(days=14),
    }


def get_hotel_room_unavailable_data():
    """Фикстура данных периода недоступности номера отеля"""
    return {
        "reason": "Ремонт",
        "start_date": timezone.now().date(),
        "end_date": timezone.now().date() + timezone.timedelta(days=7),
    }


def get_hotel_room_photo_data(room):
    """Фикстура данных фотографии номера отеля"""
    test_image = create_test_image()
    return {
        "room": room,
        "photo": test_image,
    }
