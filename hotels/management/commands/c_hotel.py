import os
import random
import uuid
from collections import defaultdict
from datetime import date, time, timedelta

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from all_fixture.choices import (
    PlaceChoices,
    RoleChoices,
    RoomCategoryChoices,
    StatusChoices,
    TypeOfHolidayChoices,
    TypeOfMealChoices,
    WhatAboutChoices,
)
from applications.models import (
    ApplicationHotel,
    ApplicationTour,
)
from calendars.models import CalendarDate, CalendarPrice
from flights.models import Flight
from guests.models import Guest
from hotels.models import Hotel, HotelPhoto, HotelWhatAbout, TypeOfMeal
from rooms.models import Room, RoomPhoto
from tours.models import Tour
from users.models import User
from vzhuhs.models import Vzhuh, VzhuhPhoto


class Command(BaseCommand):
    help = "Команда по добавлению рандомной инфы по всем сущностям"

    @staticmethod
    def calculate_insurance(guest_len):
        """
        Функция для расчета страховок (виза, медицинская страховка, страховка от отмены).
        Возвращает словарь с параметрами страховок.
        """
        if random.random() < 0.77:
            visa_count = None
            visa_price_per_one = None
            visa_total_price = None
        else:
            visa_count = guest_len
            visa_price_per_one = round(random.uniform(4000, 6000), 2)
            visa_total_price = visa_price_per_one * visa_count

        if random.random() < 0.77:
            med_insurance_count = None
            med_insurance_price_per_one = None
            med_insurance_total_price = None
        else:
            med_insurance_count = guest_len
            med_insurance_price_per_one = round(random.uniform(4000, 6000), 2)
            med_insurance_total_price = med_insurance_price_per_one * med_insurance_count

        if random.random() < 0.77:
            cancellation_insurance_total = None
        else:
            cancellation_insurance_total = round(random.uniform(4000, 6000), 2)

        return {
            "visa_count": visa_count,
            "visa_price_per_one": visa_price_per_one,
            "visa_total_price": visa_total_price,
            "med_insurance_count": med_insurance_count,
            "med_insurance_price_per_one": med_insurance_price_per_one,
            "med_insurance_total_price": med_insurance_total_price,
            "cancellation_insurance_total": cancellation_insurance_total,
        }

    @staticmethod
    def generate_random_date(start_month, end_month, year):
        """Функиця для генерации случайных дат в диапазоне."""
        month = random.randint(start_month, end_month)
        if month == 2:
            day = random.randint(1, 28)
        elif month in [4, 6, 9, 11]:
            day = random.randint(1, 30)
        else:
            day = random.randint(1, 31)
        return date(year=year, month=month, day=day)

    @staticmethod
    def generate_random_price(min_price=3000, max_price=99999):
        """Функция для генерации случайных цен в диапазоне от min_price до max_price."""
        return round(random.uniform(min_price, max_price), 2)

    @staticmethod
    def generate_discount_amount():
        """Функция генерации случайного значения discount_amount."""
        if random.choice([True, False]):
            return round(random.uniform(0.01, 0.99), 2)
        else:
            return round(random.uniform(1000, 5000), 2)

    @staticmethod
    def generate_arrival_time(dep_time, same_day=True):
        """Генерирует реалистичное время прибытия"""
        if same_day:
            arr_hour = random.randint(dep_time.hour, 23)
            if arr_hour == dep_time.hour:
                arr_min = random.randint(dep_time.minute + 1, 59)
            else:
                arr_min = random.choice([0, 15, 30, 45])
        else:
            arr_hour = random.randint(0, 23)
            arr_min = random.choice([0, 15, 30, 45])

        return time(arr_hour, arr_min)

    @staticmethod
    def add_photos_fk(
        instances,
        dir_path,
        photo_model,
        fk_name,
        count,
    ):
        files = os.listdir(dir_path)
        for obj in instances:
            for _ in range(count):
                filename = random.choice(files)
                full_path = os.path.join(dir_path, filename)
                with open(full_path, "rb") as f:
                    django_file = File(f, name=filename)
                    photo_model.objects.create(**{fk_name: obj}, photo=django_file)

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Создание админка
            self.create_admin()
            # Создание туроператора
            tour_operators = self.create_tour_operators()
            # Создание туриста
            tourists = self.create_tourists()
            # Создание гостей у туристов
            total_guests = 0
            all_guests = []
            for tourist in tourists:
                guests = self.create_guests(tourist)
                total_guests += len(guests)
                all_guests.extend(guests)
            # Создание отелей, типов питания, номеров, стоимости номеров по датам, рейсов, туров
            hotels = self.create_test_hotels(50)
            type_of_meals = self.create_type_of_meals(hotels)
            rooms = self.create_test_rooms(hotels)
            self.create_room_prices(hotels)
            flights = self.create_flights()
            tours = self.create_test_tours(flights, hotels)
            # Создание подборки, что насчёт
            what_abouts = self.create_what_about(hotels)
            # Создание заявок на туры и отели
            applications = self.create_applications(
                tours,
                hotels,
                rooms,
                tourists,
                all_guests,
            )
            self.create_vzhuhs()
            self.print_success_message(
                len(tour_operators),
                len(hotels),
                len(type_of_meals),
                len(rooms),
                len(flights),
                len(tours),
                len(tourists),
                total_guests,
                len(what_abouts),
                len(applications),
            )

    def create_admin(self):
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")

        # Проверяем, существует ли уже администратор с указанным именем пользователя
        if not User.objects.filter(email=os.getenv("ADMIN_EMAIL")).exists():
            user = User.objects.create_superuser(
                email=email,
                first_name="Admin",
                last_name="Admin",
                role=RoleChoices.ADMIN,
            )
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f"=== ADMIN с таким email {os.getenv('ADMIN_EMAIL')} успешно создан ===")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"=== ADMIN с таким email {os.getenv('ADMIN_EMAIL')} уже существует ===")
            )

    def create_tour_operators(self):
        name_to_surname = {
            "Никита": "ТимаБэков",
            "Тимофей": "ТимаФронтов",
        }
        operators = []
        for i, (first_name, last_name) in enumerate(name_to_surname.items()):
            company_name = f"ООО Тима {last_name[4:]}"
            email = f"operator.{i + 1}{uuid.uuid4()}@mail.ru"
            phone_number = f"+7995{random.randint(1000000, 9999999)}"
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                password="123456",
                company_name=company_name,
                role=RoleChoices.TOUR_OPERATOR,
            )
            operators.append(user)
        return operators

    def create_tourists(self):
        name_to_surname = {
            "Татьяна": "ПМ",
            "Вячеслав": "ПМ",
            "Марина": "QA",
            "Оксана": "QA",
        }
        tourists = []
        for i, (first_name, last_name) in enumerate(name_to_surname.items()):
            email = f"tourists.{i + 1}{uuid.uuid4()}@mail.ru"
            phone_number = f"+7926{random.randint(1000000, 9999999)}"
            birth_date = date(
                random.randint(2000, 2004),
                random.randint(1, 12),
                random.randint(1, 28),
            )
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                birth_date=birth_date,
                password="123456",
                role=RoleChoices.USER,
            )
            tourists.append(user)
        return tourists

    def create_guests(self, tourist):
        name_to_surname_back = {
            "Никита": "Бэкендов",
            "Евгений": "Бэкендов",
            "Максим": "Бэкендов",
            "Дмитрий": "Бэкендов",
            "Александр": "Бэкендов",
            "Андрей": "Бэкендов",
            "Виктория": "Бэкендова",
            "Мария": "Бэкендова",
            "Елена": "Бэкендова",
            "Анна": "Бэкендова",
        }
        name_to_surname_front = {
            "Тимофей": "Фронтендов",
            "Егор": "Фронтендов",
            "Игорь": "Фронтендов",
            "Артем": "Фронтендов",
            "Владислав": "Фронтендов",
            "Екатерина": "Фронтендова",
            "Анастасия": "Фронтендова",
            "Ольга": "Фронтендова",
            "София": "Фронтендова",
            "Полина": "Фронтендова",
        }

        guests = []
        if tourist.last_name == "ПМ":
            names_dict = name_to_surname_back
        else:
            names_dict = name_to_surname_front

        num_guests = random.randint(2, 3)
        selected_names = random.sample(
            list(names_dict.items()),
            min(num_guests, len(names_dict)),
        )

        for first_name, last_name in selected_names:
            date_born = date(
                random.randint(1991, 2004),
                random.randint(1, 12),
                random.randint(1, 28),
            )
            ru_passport = f"{random.randint(1000, 9999)} {random.randint(100000, 999999)}"
            int_passport = f"{random.randint(10, 99)} {random.randint(1000000, 9999999)}"
            int_passport_valid = date(
                random.randint(2025, 2035),
                random.randint(1, 12),
                random.randint(1, 28),
            )
            guest = Guest.objects.create(
                firstname=first_name,
                lastname=last_name,
                surname="Кудоугодновичи",
                date_born=date_born,
                citizenship="РФ",
                russian_passport_no=ru_passport,
                international_passport_no=int_passport,
                validity_international_passport=int_passport_valid,
                user_owner=tourist,
            )
            guests.append(guest)
        return guests

    def create_test_hotels(self, count):
        places = [choice[0] for choice in PlaceChoices.choices]
        types_of_holiday = [choice[0] for choice in TypeOfHolidayChoices.choices]
        amenities_common = ["Общие", "Общие 2", "Общие 3"]
        amenities_in_the_room = ["В номере", "В номере 2", "В номере 3"]
        amenities_sports_and_recreation = ["Зал", "Фитнес"]
        amenities_for_children = ["Аквапарк", "Детская площадка", "Аниматоры"]

        countries_cities = {
            "Турция": ["Анталия", "Стамбул", "Измир"],
            "Греция": ["Афины", "Салоники", "Ираклион"],
            "Франция": ["Париж", "Ницца", "Марсель"],
            "Италия": ["Рим", "Милан", "Венеция"],
            "Испания": ["Мадрид", "Барселона", "Валенсия"],
            "Кипр": ["Лимассол", "Никосия", "Пафос"],
            "Россия": ["Москва", "Санкт-Петербург"],
            "ОАЭ": ["Дубай", "Абу-Даби", "Шарджа"],
            "Таиланд": ["Бангкок", "Паттайя", "Пхукет"],
            "Египет": ["Каир", "Хургада", "Шарм-эш-Шейх"],
            "Индонезия": ["Джакарта", "Денпасар (Бали)", "Сурабая"],
            "Вьетнам": ["Ханой", "Хошимин", "Нячанг"],
            "Мальдивы": ["Мале"],
            "Доминикана": ["Пунта-Кана", "Санто-Доминго"],
            "Черногория": ["Будва", "Котор", "Подгорица"],
            "Тунис": ["Тунис", "Сусс", "Хаммамет"],
            "Мексика": ["Мехико", "Канкун", "Плая-дель-Кармен"],
        }

        rules = {
            "С животными": "Можно если за ними следить",
            "Бухать": "Можно если за Вами следит жена",
        }
        # Пути к тестовым фотографиям отелей
        hotel_photos_dir = os.path.join(
            settings.BASE_DIR,
            "static",
            "test_hotel",
        )

        hotels = []
        for i in range(count):
            country = random.choice(list(countries_cities.keys()))
            city = random.choice(countries_cities[country])
            hotel = Hotel.objects.create(
                name=f"Отель в {city} {i + 1}",
                star_category=random.randint(1, 5),
                place=random.choice(places),
                country=country,
                city=city,
                address=f"Ул. Пушкина, д. {i + 1}",
                distance_to_the_station=random.randint(0, 50000),
                distance_to_the_sea=random.randint(0, 50000),
                distance_to_the_center=random.randint(0, 50000),
                distance_to_the_metro=random.randint(0, 50000),
                distance_to_the_airport=random.randint(0, 50000),
                description=f"Так себе описание отеля под номером {i + 1}",
                check_in_time=time(random.randint(14, 16), 0),
                check_out_time=time(random.randint(10, 12), 0),
                amenities_common=random.sample(
                    amenities_common,
                    k=random.randint(1, len(amenities_common)),
                ),
                amenities_in_the_room=random.sample(
                    amenities_in_the_room,
                    k=random.randint(1, len(amenities_in_the_room)),
                ),
                amenities_sports_and_recreation=random.sample(
                    amenities_sports_and_recreation,
                    k=random.randint(1, len(amenities_sports_and_recreation)),
                ),
                amenities_for_children=random.sample(
                    amenities_for_children,
                    k=random.randint(1, len(amenities_for_children)),
                ),
                user_rating=round(random.uniform(2, 9), 1),
                type_of_rest=random.choice(types_of_holiday),
                is_active=random.choice([True, False]),
                width=round(random.uniform(-90, 90), 6),
                longitude=round(random.uniform(-180, 180), 6),
            )
            hotels.append(hotel)

            for rule_name, rule_description in rules.items():
                hotel.rules.create(
                    hotel=hotel,
                    name=rule_name,
                    description=rule_description,
                )
        self.add_photos_fk(
            hotels,
            hotel_photos_dir,
            HotelPhoto,
            "hotel",
            5,
        )
        return hotels

    def create_type_of_meals(self, hotels):
        """
        Для каждого отеля создаём все доступные типы питания с рандомной ценой,
        где каждый следующий тип питания стоит больше, чем предыдущий.
        """
        type_of_meals = []
        basic_types = [
            TypeOfMealChoices.BREAKFAST,
            TypeOfMealChoices.BREAKFAST_AND_DINNER,
            TypeOfMealChoices.FULL_BOARD,
        ]
        premium_types = [
            TypeOfMealChoices.ALL_INCLUSIVE,
            TypeOfMealChoices.ULTRA_ALL_INCLUSIVE,
        ]
        for hotel in hotels:
            # Создаем словарь для хранения цен предыдущих типов питания
            meal_prices = {}
            for meal_name in [choice[0] for choice in TypeOfMealChoices.choices]:
                if meal_name == TypeOfMealChoices.NO_MEAL:
                    price = 0
                elif meal_name in basic_types:
                    if meal_name == TypeOfMealChoices.BREAKFAST:
                        price = round(random.uniform(1000, 5001) / 500) * 500
                    elif meal_name == TypeOfMealChoices.BREAKFAST_AND_DINNER:
                        price = meal_prices.get(TypeOfMealChoices.BREAKFAST, 0) + random.choice(range(500, 5001, 500))
                    elif meal_name == TypeOfMealChoices.FULL_BOARD:
                        price = (
                            meal_prices.get(
                                TypeOfMealChoices.BREAKFAST_AND_DINNER,
                                meal_prices.get(TypeOfMealChoices.BREAKFAST, 0),
                            )
                            + round(random.uniform(1000, 5001) / 500) * 500
                        )
                elif meal_name in premium_types:
                    if meal_name == TypeOfMealChoices.ALL_INCLUSIVE:
                        price = round(random.uniform(1000, 100001) / 1000) * 1000
                    elif meal_name == TypeOfMealChoices.ULTRA_ALL_INCLUSIVE:
                        price = meal_prices.get(TypeOfMealChoices.ALL_INCLUSIVE, 0) + random.choice(
                            range(1000, 100001, 1000)
                        )
                else:
                    price = round(random.uniform(1000, 50001) / 500) * 500
                # Сохраняем цену текущего типа питания
                meal_prices[meal_name] = price
                type_of_meal = TypeOfMeal.objects.create(
                    hotel=hotel,
                    name=meal_name,
                    price=price,
                )
                type_of_meals.append(type_of_meal)
        return type_of_meals

    def create_test_rooms(
        self,
        hotels,
        count=5,
    ):
        room_categories = [choice[0] for choice in RoomCategoryChoices.choices]
        amenities_common = ["WiFi", "ТВ", "Минибар", "Кондиционер"]
        amenities_coffee = ["Кофе машина в номере", "Чайный сет"]
        amenities_bathroom = ["Душевые принадлежности", "Фен"]
        amenities_view = ["Море", "Горы", "Сад"]
        rules_names = [
            "Курить",
            "С животными",
            "Алкоголь",
        ]

        room_photos_dir = os.path.join(
            settings.BASE_DIR,
            "static",
            "test_room",
        )

        rooms = []
        for hotel in hotels:
            for _iteration_bed in range(count):
                number_of_adults = random.randint(2, 4)
                number_of_children = random.randint(0, 4)
                # Кровати для взрослых
                if number_of_adults == 2:
                    double_bed = 1
                    single_bed = 0
                elif number_of_adults == 3:
                    double_bed = 1
                    single_bed = 1
                elif number_of_adults == 4:
                    double_bed = 1
                    single_bed = 2
                else:
                    double_bed = 1
                    single_bed = 0
                # Кровати для детей
                if number_of_children > 0:
                    single_bed += number_of_children

                room = Room.objects.create(
                    hotel=hotel,
                    category=random.choice(room_categories),
                    number_of_adults=number_of_adults,
                    number_of_children=number_of_children,
                    single_bed=single_bed,
                    double_bed=double_bed,
                    area=random.randint(20, 100),
                    quantity_rooms=random.randint(1, 10),
                    amenities_common=random.sample(
                        amenities_common,
                        k=random.randint(1, len(amenities_common)),
                    ),
                    amenities_coffee=random.sample(
                        amenities_coffee,
                        k=random.randint(0, len(amenities_coffee)),
                    ),
                    amenities_bathroom=random.sample(
                        amenities_bathroom,
                        k=random.randint(1, len(amenities_bathroom)),
                    ),
                    amenities_view=random.sample(
                        amenities_view,
                        k=random.randint(1, len(amenities_view)),
                    ),
                )
                for rule_name in rules_names:
                    room.rules.create(
                        name=rule_name,
                        option=random.choice([True, False]),
                    )

                rooms.append(room)

        self.add_photos_fk(
            rooms,
            room_photos_dir,
            RoomPhoto,
            "room",
            6,
        )

        return rooms

    def create_room_prices(self, hotels):
        for hotel in hotels:
            rooms = list(hotel.rooms.all())
            num_dates = random.randint(1, 5)
            current_start_date = self.generate_random_date(
                start_month=8,
                end_month=12,
                year=2025,
            )

            for _ in range(num_dates):
                discount = random.choice([True, False])
                end_date = current_start_date + timedelta(days=random.randint(10, 14))
                discount_amount = self.generate_discount_amount() if discount else None
                calendar_date = CalendarDate.objects.create(
                    hotel=hotel,
                    start_date=current_start_date,
                    end_date=end_date,
                    available_for_booking=True,
                    discount=discount,
                    discount_amount=discount_amount,
                )

                num_rooms_for_date = random.randint(
                    1,
                    min(10, len(rooms)),
                )
                selected_rooms = random.sample(
                    rooms,
                    k=num_rooms_for_date,
                )

                calendar_price = [
                    CalendarPrice(
                        calendar_date=calendar_date,
                        room=room,
                        price=self.generate_random_price(),
                    )
                    for room in selected_rooms
                ]
                CalendarPrice.objects.bulk_create(calendar_price)
                current_start_date = end_date + timedelta(days=1)

    def create_flights(self):
        """
        Создаёт по два рейса для каждого отеля за пределами России:
        — рейс туда (Москва → город отеля)
        — рейс обратно (город отеля → Москва) через 7 дней
        Возвращает список всех созданных Flight.
        """
        arrival_city_airport = {
            # Турция
            "Анталия": "AYT",
            "Стамбул": "IST",
            "Измир": "ADB",
            # Греция
            "Афины": "ATH",
            "Салоники": "SKG",
            "Ираклион": "HER",
            # Франция
            "Париж": "CDG",
            "Ницца": "NCE",
            "Марсель": "MRS",
            # Италия
            "Рим": "FCO",
            "Милан": "MXP",
            "Венеция": "VCE",
            # Испания
            "Мадрид": "MAD",
            "Барселона": "BCN",
            "Валенсия": "VLC",
            # Кипр
            "Лимассол": "LCL",
            "Никосия": "NIC",
            "Пафос": "PFO",
            # Египет
            "Шарм-Эль-Шейх": "SSH",
        }

        city_to_country = {
            # Турция
            "Анталия": "Турция",
            "Стамбул": "Турция",
            "Измир": "Турция",
            # Греция
            "Афины": "Греция",
            "Салоники": "Греция",
            "Ираклион": "Греция",
            # Франция
            "Париж": "Франция",
            "Ницца": "Франция",
            "Марсель": "Франция",
            # Италия
            "Рим": "Италия",
            "Милан": "Италия",
            "Венеция": "Италия",
            # Испания
            "Мадрид": "Испания",
            "Барселона": "Испания",
            "Валенсия": "Испания",
            # Кипр
            "Лимассол": "Кипр",
            "Никосия": "Кипр",
            "Пафос": "Кипр",
            # Египет
            "Шарм-Эль-Шейх": "Египет",
        }

        flight_numbers = [
            f"AT-{random.randint(1000, 9999)}",
            f"TT-{random.randint(1000, 9999)}",
            f"TQ-{random.randint(1000, 9999)}",
            f"TS-{random.randint(1000, 9999)}",
        ]
        airlines = ["Azure", "Аэрофлот"]
        service_classes = ["Эконом", "Бизнес", "Первый"]
        flight_types = ["Регулярный", "Чартерный"]
        descriptions = ["Багаж включен", "Багаж не включен"]

        created_flights = []

        # Перебираем все отели за пределами России
        for hotel in Hotel.objects.exclude(country="Россия").iterator():
            city = hotel.city
            # Пропускаем, если нет аэропорта для этого города
            if city not in arrival_city_airport:
                continue

            arrival_country = city_to_country.get(city, "Неизвестно")

            # --- Рейс туда ---
            dep_date = date(
                year=2025,
                month=9,
                day=random.randint(1, 24),
            )
            dep_time = time(
                hour=random.randint(0, 23),
                minute=random.choice([0, 15, 30, 45]),
            )
            arrival_time = self.generate_arrival_time(dep_time, same_day=True)
            price = round(random.uniform(1000, 10000), 2)
            price_for_child = round(price / 2, 2) if random.random() > 0.3 else None

            flight_to = Flight.objects.create(
                flight_number=random.choice(flight_numbers),
                airline=random.choice(airlines),
                departure_country="Россия",
                departure_city="Москва",
                departure_airport="SVO",
                arrival_country=arrival_country,
                arrival_city=city,
                arrival_airport=arrival_city_airport[city],
                departure_date=dep_date,
                departure_time=dep_time,
                arrival_date=dep_date,
                arrival_time=arrival_time,
                price=price,
                price_for_child=price_for_child,
                service_class=random.choice(service_classes),
                flight_type=random.choice(flight_types),
                description=random.choice(descriptions),
            )
            created_flights.append(flight_to)

            # --- Рейс обратно через 7 дней ---
            return_date = dep_date + timedelta(days=7)
            return_dep_time = time(
                hour=random.randint(0, 23),
                minute=random.choice([0, 15, 30, 45]),
            )
            return_arrival_time = self.generate_arrival_time(
                return_dep_time,
                same_day=True,
            )
            # Генерация цены и цены для ребенка для обратного рейса
            price_back = round(random.uniform(1000, 10000), 2)
            price_for_child_back = round(price_back / 2, 2) if random.random() > 0.3 else None

            flight_back = Flight.objects.create(
                flight_number=random.choice(flight_numbers),
                airline=random.choice(airlines),
                departure_country=arrival_country,  # Новое поле
                departure_city=city,
                departure_airport=arrival_city_airport[city],
                arrival_country="Россия",
                arrival_city="Москва",
                arrival_airport="SVO",
                departure_date=return_date,
                departure_time=return_dep_time,
                arrival_date=return_date,
                arrival_time=return_arrival_time,
                price=price_back,
                price_for_child=price_for_child_back,
                service_class=random.choice(service_classes),
                flight_type=random.choice(flight_types),
                description=random.choice(descriptions),
            )
            created_flights.append(flight_back)

        return created_flights

    def create_test_tours(
        self,
        flights,
        hotels,
        count=50,
    ):
        """
        Генерация тестовых туров.
        :param flights: список всех созданных Flight
        :param hotels: список Hotel
        :param count: желаемое число туров
        :return: список созданных Tour
        """
        tours = []
        operators = list(User.objects.filter(role="TOUR_OPERATOR")[:5])

        for _ in range(count):
            # Выбираем пару «туда» и «обратно»
            flight_to = random.choice([f for f in flights if f.departure_city == "Москва"])
            flight_back = random.choice(
                [f for f in flights if f.arrival_city == "Москва" and f.arrival_date > flight_to.departure_date],
            )
            # Даты тура — от вылета до возвращения
            start = flight_to.departure_date
            end = flight_back.departure_date

            hotel = random.choice(hotels)

            # Выбираем случайное количество номеров (от 1 до 3, если доступно)
            available_rooms = list(hotel.rooms.all())
            num_rooms = random.randint(1, min(3, len(available_rooms))) if available_rooms else 0
            selected_rooms = random.sample(available_rooms, num_rooms) if num_rooms > 0 else []

            # Выбираем типы питания: по одному на каждый номер, с возможностью повторов
            available_meals = list(hotel.type_of_meals.all())
            selected_meals = (
                [random.choice(available_meals) for _ in range(num_rooms)]
                if available_meals and selected_rooms
                else []
            )

            operator = random.choice(operators) if operators else None

            if random.random() < 0.77:
                discount_amount = None
                discount_start_date = None
                discount_end_date = None
            else:
                discount_amount = self.generate_discount_amount()
                discount_start_date = start + timedelta(days=1)
                discount_end_date = end - timedelta(days=1)

            markup_amount = self.generate_discount_amount()
            publish_start_date = start - timedelta(days=28)
            publish_end_date = end - timedelta(days=1)

            tour = Tour.objects.create(
                start_date=start,
                end_date=end,
                flight_to=flight_to,
                flight_from=flight_back,
                departure_country="Россия",
                departure_city="Москва",
                arrival_country=hotel.country,
                arrival_city=hotel.city,
                tour_operator=operator,
                hotel=hotel,
                transfer=random.choice([True, False]),
                total_price=round(random.uniform(50000, 200000), 2),
                discount_amount=discount_amount,
                discount_start_date=discount_start_date,
                discount_end_date=discount_end_date,
                markup_amount=markup_amount,
                publish_start_date=publish_start_date,
                publish_end_date=publish_end_date,
                is_active=random.choice([True, False]),
            )
            tours.append(tour)
            if selected_rooms:
                tour.rooms.set(selected_rooms)
            if selected_meals:
                tour.type_of_meals.set(selected_meals)

        return tours

    def create_what_about(self, hotels):
        what_abouts = []
        for name, _ in WhatAboutChoices.choices:
            for _ in range(5):
                selected_hotels = random.sample(hotels, k=min(3, len(hotels)))
                what_about = HotelWhatAbout.objects.create(
                    name_set=name,
                )
                for hotel in selected_hotels:
                    what_about.hotel.add(hotel)
                what_abouts.append(what_about)
        return what_abouts

    def create_applications(
        self,
        tours,
        hotels,
        rooms,
        tourists,
        guests,
    ):
        """
        Функция для создания тестовых заявок (ApplicationHotel и ApplicationTour).
        Возвращает список созданных заявок.
        """
        if not tourists or not hotels or not tours:
            return []  # Проверка на наличие данных

        # Создание словаря гостей по туристам для быстрого доступа
        guest_map = defaultdict(list)
        for g in guests:
            guest_map[g.user_owner].append(g)

        applications = []
        wishes_samples = [
            "Нужен ранний заезд",
            "Просим вид на море",
            "Без животных",
            "Тихий номер",
            "Близко к лифту",
            "Высокий этаж",
            "Дополнительные полотенца",
            "Поздний выезд",
            "",
        ]

        for i in range(10):
            tourist = random.choice(tourists)
            user_guests = guest_map[tourist]
            if not user_guests:
                continue

            selected_guests = random.sample(
                user_guests,
                k=min(
                    random.randint(2, 4),
                    len(user_guests),
                ),
            )
            guest_len = len(selected_guests)

            email = f"application.{i + 1}{uuid.uuid4()}@mail.ru"
            phone_number = f"+7915{random.randint(1000000, 9999999)}"
            wishes = random.choice(wishes_samples)
            status = StatusChoices.AWAIT_CONFIRM

            # Генерация базовой цены для каждой заявки
            base_price = round(random.uniform(30000, 150000), 2)

            # Расчет страховок
            insurance = self.calculate_insurance(guest_len)

            # Расчет общей стоимости
            total_price = (
                base_price
                + (insurance["visa_total_price"] or 0)
                + (insurance["med_insurance_total_price"] or 0)
                + (insurance["cancellation_insurance_total"] or 0)
            )

            if i < 5:
                hotel = random.choice(hotels)
                valid_rooms = [r for r in rooms if r.hotel == hotel]
                if not valid_rooms:
                    continue
                room = random.choice(valid_rooms)

                application = ApplicationHotel.objects.create(
                    email=email,
                    phone_number=phone_number,
                    wishes=wishes if wishes else None,
                    status=status,
                    hotel=hotel,
                    room=room,
                    price=total_price,
                    **insurance,
                )
            else:
                tour = random.choice(tours)
                application = ApplicationTour.objects.create(
                    email=email,
                    phone_number=phone_number,
                    wishes=wishes if wishes else None,
                    status=status,
                    tour=tour,
                    price=total_price,
                    **insurance,
                )
            # Добавление гостей к заявке
            for guest in selected_guests:
                application.quantity_guests.add(guest)

            applications.append(application)

        return applications

    def create_vzhuhs(self):
        """Создает записи Вжухов на основе существующих отелей и туров."""

        # Получаем все города, для которых есть и отели, и туры
        hotel_cities = set(
            Hotel.objects.values_list(
                "city",
                flat=True,
            ).distinct()
        )
        tour_cities = set(
            Tour.objects.values_list(
                "arrival_city",
                flat=True,
            ).distinct()
        )
        common_cities = hotel_cities.intersection(tour_cities)

        # Базовые города вылета
        departure_cities = [
            "Москва",
            "Санкт-Петербург",
            "Екатеринбург",
            "Новосибирск",
            "Казань",
        ]

        # Путь к фотографиям
        photo_dir = os.path.join("static", "test_vzhuh")

        try:
            # Получаем список файлов фотографий
            photo_files = [f for f in os.listdir(photo_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Директория {photo_dir} не найдена"))
            return

        if not photo_files:
            self.stdout.write(self.style.ERROR("В директории нет фотографий"))
            return

        created_count = 0

        for arrival_city in common_cities:
            # Пропускаем города с пустыми названиями
            if not arrival_city:
                continue

            # Выбираем случайный город вылета
            departure_city = random.choice(departure_cities)

            # Проверяем, существует ли уже такой Вжух
            if Vzhuh.objects.filter(departure_city=departure_city, arrival_city=arrival_city).exists():
                continue

            hotels_count = Hotel.objects.filter(city=arrival_city).count()
            tours_count = Tour.objects.filter(arrival_city=arrival_city).count()

            if hotels_count < 3 or tours_count < 3 or len(photo_files) < 3:
                self.stdout.write(
                    self.style.WARNING(
                        f"Пропуск города {arrival_city}: недостаточно данных "
                        f"(отели: {hotels_count}, туры: {tours_count}, фото: {len(photo_files)})"
                    )
                )
                continue

            # Создаем Вжух
            vzhuh = Vzhuh.objects.create(
                departure_city=departure_city,
                arrival_city=arrival_city,
                description=f"Отличное предложение в {arrival_city}",
                best_time_to_travel="Круглый год",
                suitable_for_whom="Для всех категорий туристов",
                description_hotel=f"Лучшие отели в {arrival_city}",
                description_blog=f"Интересные места в {arrival_city}",
                is_published=True,
            )

            # Добавляем 3 случайные фотографии
            selected_photos = random.sample(photo_files, 3)
            for photo_name in selected_photos:
                photo_path = os.path.join(photo_dir, photo_name)
                with open(photo_path, "rb") as f:
                    django_file = File(f, name=os.path.basename(photo_path))
                    photo = VzhuhPhoto(photos=django_file)
                    photo.save()
                    vzhuh.photos.add(photo)

            # Добавляем 3 случайных отеля
            hotels = list(Hotel.objects.filter(city=arrival_city))
            selected_hotels = random.sample(hotels, 3)
            vzhuh.hotels.add(*selected_hotels)

            # Добавляем 3 случайных тура
            tours = list(Tour.objects.filter(arrival_city=arrival_city))
            selected_tours = random.sample(tours, 3)
            vzhuh.tours.add(*selected_tours)

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Создано {created_count} записей Вжухов"))

    def print_success_message(
        self,
        tour_operators_count,
        hotels_count,
        type_of_meals_count,
        rooms_count,
        flights_count,
        tours_count,
        tourists_count,
        total_guests,
        what_abouts_count,
        applications_count,
    ):
        self.stdout.write(
            self.style.SUCCESS(
                f"Успешно создано:\n"
                f"- {tour_operators_count} туроператоров\n"
                f"- {hotels_count} отелей c 4 фото в каждом\n"
                f"- {type_of_meals_count} кол-во типов питания\n"
                f"- {rooms_count} номеров с 6 фото каждом\n"
                f"- {flights_count} рейсов\n"
                f"- {tours_count} туров\n"
                f"- {tourists_count} туристов\n"
                f"- {total_guests} гостей\n"
                f"- {what_abouts_count} подборок Что насчёт...\n"
                f"- {applications_count} заявок"
            )
        )
