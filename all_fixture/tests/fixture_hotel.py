from datetime import time

from all_fixture.tests.test_temp_image import create_test_image


def get_hotel_data():
    """Фикстура отеля"""
    return {
        "name": "Тестовый отель",
        "star_category": 5,
        "place": "Отель",
        "country": "Россия",
        "city": "Москва",
        "address": "ул. Пушкина, д. 1",
        "distance_to_the_station": 3500,
        "distance_to_the_sea": 20000,
        "distance_to_the_center": 2000,
        "distance_to_the_metro": 1500,
        "distance_to_the_airport": 3000,
        "description": "Тестовое описание",
        "check_in_time": time(14, 0, 0),
        "check_out_time": time(12, 0, 0),
        "amenities_common": ["Wi-Fi", "Парковка"],
        "amenities_in_the_room": ["ТВ", "Мини-бар"],
        "amenities_sports_and_recreation": ["Бассейн", "Тренажёрный зал"],
        "amenities_for_children": ["Детская площадка"],
        "type_of_meals_ultra_all_inclusive": 5000,
        "type_of_meals_all_inclusive": 4000,
        "type_of_meals_full_board": 3000,
        "type_of_meals_half_board": 2000,
        "type_of_meals_only_breakfast": 1000,
        "user_rating": 8.5,
        "type_of_rest": "Пляжный",
        "is_active": True,
        "room_categories": ["Стандарт", "Делюкс"],
    }


def update_hotel_data():
    """Фикстура обновлённых полей отеля"""
    return {
        "name": "Обновлённый тестовый отель",
        "star_category": 4,
        "place": "Отель",
        "country": "Россия",
        "city": "Москва",
        "address": "ул. Пушкина, д. 1",
        "distance_to_the_station": 3500,
        "distance_to_the_sea": 20000,
        "distance_to_the_center": 2000,
        "distance_to_the_metro": 1500,
        "distance_to_the_airport": 3000,
        "description": "Тестовое описание",
        "check_in_time": time(14, 0, 0),
        "check_out_time": time(12, 0, 0),
        "amenities_common": ["Wi-Fi", "Парковка"],
        "amenities_in_the_room": ["ТВ", "Мини-бар"],
        "amenities_sports_and_recreation": ["Бассейн", "Тренажёрный зал"],
        "amenities_for_children": ["Детская площадка"],
        "type_of_meals_ultra_all_inclusive": 5000,
        "type_of_meals_all_inclusive": 4000,
        "type_of_meals_full_board": 3000,
        "type_of_meals_half_board": 2000,
        "type_of_meals_only_breakfast": 1000,
        "user_rating": 8.9,
        "type_of_rest": "Пляжный",
        "is_active": True,
        "room_categories": ["Стандарт", "Люкс"],
    }


def get_hotel_photo_data(hotel):
    """Фикстура фотографии отеля"""
    test_image = create_test_image()
    return {
        "hotel": hotel,
        "photo": test_image,
    }


def get_hotel_rules_data(hotel):
    """Фикстура правил отеля"""
    return {
        "hotel": hotel,
        "name": "Тестовое название правила",
        "description": "Тестовое описание правила",
    }
