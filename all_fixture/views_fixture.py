from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from all_fixture.choices import CountryChoices
from blogs.constants import (
    MAX_PHOTO_SIZE_MB,
    MAX_PHOTOS,
    MAX_VIDEO_DURATION,
    MAX_VIDEO_SIZE_MB,
    MAX_VIDEOS,
)

NULLABLE = {"blank": True, "null": True}
# Теги для settings
USER_SETTINGS = {
    "name": "Пользователи",
    "description": "Методы для работы с пользователями",
}
ENTREPRISE_SETTINGS = {
    "name": "Компании",
    "description": "Методы для работы с компаниями",
}
AUTH_SETTINGS = {
    "name": "Авторизация",
    "description": "Методы для работы с авторизацией",
}
TOUR_SETTINGS = {
    "name": "Туры",
    "description": "Методы для работы с турами",
}
HOTEL_SETTINGS = {
    "name": "Отели",
    "description": "Методы для работы с отелями",
}
HOTEL_PHOTO_SETTINGS = {
    "name": "Фотографии в отеле",
    "description": "Методы для работы с фотографиями отелей",
}
ROOM_SETTINGS = {
    "name": "Номера",
    "description": "Методы для работы с номерами",
}
ROOM_PHOTO_SETTINGS = {
    "name": "Фотографии номера",
    "description": "Методы для работы с фотографиями номеров",
}
ROOM_RULES_SETTINGS = {
    "name": "Правила номеров",
    "description": "Методы для работы с правилами номеров",
}
FLIGHT_SETTINGS = {
    "name": "Рейсы",
    "description": "Методы для работы с рейсами",
}
APPLICATION_SETTINGS = {
    "name": "Заявки",
    "description": "Методы для работы с заявками",
}
GUEST_SETTINGS = {
    "name": "Гости",
    "description": "Методы для работы с гостями",
}
INSURANCE_SETTINGS = {
    "name": "Страховки",
    "description": "Методы для работы со страховками",
}
WHAT_ABOUT_SETTINGS = {
    "name": "Что на счёт ...",
    "description": "Получаем список подборок что насчёт...",
}
TYPE_OF_MEAL_SETTINGS = {
    "name": "Тип питания",
    "description": "Методы для работы с типами питания",
}
CALENDAR_SETTINGS = {
    "name": "Календарь стоимость номеров в отеле",
    "description": "Методы для работы с календарём стоимости номеров в отеле",
}
MAILING_SETTINGS = {
    "name": "Рассылки",
    "description": "Методы для работы с рассылками",
}
DISCOUNT_SETTINGS = {
    "name": "Акции",
    "description": "Методы для работы со страницей с акциями",
}
VZHUH_SETTINGS = {
    "name": "Вжухи",
    "description": "Список актуальных спецпредложений по направлениям",
}
BLOG_SETTINGS = {
    "name": "Блог: Статьи",
    "description": "Методы для работы со статьями блога",
}
CATEGORY_SETTINGS = {
    "name": "Блог: Категории",
    "description": "Методы для работы со справочником категорий",
}
TAG_SETTINGS = {
    "name": "Блог: Теги",
    "description": "Методы для работы со справочником тегов",
}
THEME_SETTINGS = {
    "name": "Блог: Темы",
    "description": "Методы для работы со справочником тем статей",
}
COMMENTS_SETTINGS = {
    "name": "Блог: Комментарии",
    "description": "Методы для работы с комментариями к статьям",
}
LIKES_SETTINGS = {
    "name": "Блог: Реакции",
    "description": "Методы для работы с лайками/дизлайками комментариев",
}

# ID пользователя
USER_ID = OpenApiParameter(
    name="id",
    type=int,
    location=OpenApiParameter.PATH,
    description="ID Пользователя",
    required=True,
)
# ID туриста
ID_USER = OpenApiParameter(
    name="user_id",
    type=int,
    location=OpenApiParameter.PATH,
    description="ID Туриста",
    required=True,
)
# ID компании
ENTREPRISE_ID = OpenApiParameter(
    name="id",
    type=int,
    location=OpenApiParameter.PATH,
    description="ID Компании",
    required=True,
)
# ID тура
TOUR_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID Тура",
    required=True,
)
# Город вылета
TOUR_DEPARTURE_CITY = OpenApiParameter(
    name="departure_city",
    type=str,
    description="Город вылета",
    required=False,
)
# Город прилета
TOUR_ARRIVAL_CITY = OpenApiParameter(
    name="arrival_city",
    type=str,
    description="Город прилета",
    required=False,
)
# Дата вылета
TOUR_START_DATE = OpenApiParameter(
    name="start_date",
    type=str,
    description="Дата начала тура (YYYY-MM-DD)",
    required=False,
)
# Количество ночей в туре
TOUR_NIGHTS = OpenApiParameter(
    name="nights",
    type=int,
    description="Количество ночей",
    required=False,
)
# Количество гостей в туре
TOUR_GUESTS = OpenApiParameter(
    name="guests",
    type=int,
    description="Количество гостей",
    required=False,
)
# Город отеля
FILTER_CITY = OpenApiParameter(
    name="city",
    type=str,
    description="Город отеля",
    required=False,
)
# Тип размещения
FILTER_PLACE = OpenApiParameter(
    name="place",
    type=str,
    description="Тип размещения",
    required=False,
)
# Тип отдыха
FILTER_TYPE_OF_REST = OpenApiParameter(
    name="type_of_rest",
    type=str,
    description="Тип отдыха",
    required=False,
)
# Пользовательская оценка
FILTER_USER_RATING = OpenApiParameter(
    name="user_rating",
    type=float,
    description="Пользовательская оценка",
    required=False,
)
# Расстояние от отеля до аэропорта
FILTER_DISTANCE_TO_THE_AIRPORT = OpenApiParameter(
    name="distance_to_the_airport",
    type=int,
    description="Расстояние до аэропорта в метрах",
    required=False,
)
# Максимальная стоимость тура
TOUR_PRICE_LTE = OpenApiParameter(
    name="price_lte",
    type=int,
    description="Максимальная стоимость тура",
    required=False,
)
# Минимальная стоимость тура
TOUR_PRICE_GTE = OpenApiParameter(
    name="price_gte",
    type=int,
    description="Минимальная стоимость тура",
    required=False,
)
# Туроператор
FILTER_TOUR_OPERATOR = OpenApiParameter(
    name="tour_operator",
    type=str,
    description="Туроператор",
    required=False,
)
# Категория отеля в кол-ве звед
FILTER_STAR_CATEGORY = OpenApiParameter(
    name="star_category",
    type=str,
    description="Категорию отеля (от 0 до 5)",
    required=False,
)
# ID отеля
HOTEL_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="hotel_id",
    type=int,
    description="ID Отеля",
    required=False,
)
# ID типа питания
TYPE_OF_MEAL_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID типа питания",
    required=False,
)
# ID номера
ROOM_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="room_id",
    type=int,
    description="ID Номера",
    required=False,
)
# ID фотографии в номере
ROOM_ID_PHOTO = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID Фотографии номера",
    required=True,
)
# ID фотографии в отеле
HOTEL_ID_PHOTO = OpenApiParameter(
    name="id",
    type=int,
    location=OpenApiParameter.PATH,
    description="ID Фотографий отеля",
    required=True,
)
# ID в отеле
ID_HOTEL = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID Отеля",
    required=False,
)
# ID номера
ID_ROOM = OpenApiParameter(
    name="id",
    type=int,
    location=OpenApiParameter.PATH,
    description="ID Номера",
    required=True,
)
# ID Рейса
FLIGHT_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID Рейса",
    required=True,
)
# ID заявки
APPLICATION_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID Заявки",
    required=True,
)
# ID гостя
GUEST_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID Гостя в заявке",
    required=True,
)
# ID страховки
INSURANCE_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID Страховки",
    required=True,
)
# ID Календаря
CALENDAR_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID Календаря",
    required=True,
)
# Дата заезда в отель
HOTEL_CHECK_IN = OpenApiParameter(
    name="check_in_date",
    type=str,
    description="Дата заезда (YYYY-MM-DD)",
    required=False,
)
# Дата выезда из отеля
HOTEL_CHECK_OUT = OpenApiParameter(
    name="check_out_date",
    type=str,
    description="Дата выезда (YYYY-MM-DD)",
    required=False,
)
# Дата начала фильтрации в отеле номеров
HOTEL_START_DATE = OpenApiParameter(
    name="start_date",
    type=str,
    description="Дата выезда (YYYY-MM-DD)",
    required=False,
)
# Дата окончания фильтрации в отеле номеров
HOTEL_END_DATE = OpenApiParameter(
    name="end_date",
    type=str,
    description="Дата выезда (YYYY-MM-DD)",
    required=False,
)
# Количество гостей в отеле(Обязательный)
HOTEL_GUESTS = OpenApiParameter(
    name="guests",
    type=int,
    description="Количество гостей",
    required=False,
)
# Название отеля
HOTEL_CITY = OpenApiParameter(
    name="hotel_city",
    type=str,
    description="Название города",
    required=False,
)
# Дата заезда в отель(Необязательный)
HOTEL_CHECK_IN_OPTIONAL = OpenApiParameter(
    name="check_in_date",
    type=str,
    description="Дата заезда (YYYY-MM-DD)",
    required=False,
)
# Дата выезда из отеля(Необязательный)
HOTEL_CHECK_OUT_OPTIONAL = OpenApiParameter(
    name="check_out_date",
    type=str,
    description="Дата выезда (YYYY-MM-DD)",
    required=False,
)
# Количество гостей в отеле(Необязательный)
HOTEL_GUESTS_OPTIONAL = OpenApiParameter(
    name="guests",
    type=int,
    description="Количество гостей",
    required=False,
)
# Максимальная стоимость отеля
HOTEL_PRICE_LTE = OpenApiParameter(
    name="price_lte",
    type=int,
    description="Максимальная стоимость отеля",
    required=False,
)
# Минимальная стоимость отеля
HOTEL_PRICE_GTE = OpenApiParameter(
    name="price_gte",
    type=int,
    description="Минимальная стоимость отеля",
    required=False,
)
# ID рассылки
MAILING_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID Рассылки",
    required=True,
)
# Рейс страна вылета
FLIGHT_DEPARTURE_COUNTRY = OpenApiParameter(
    name="departure_country",
    type=str,
    description="Страна вылета",
    required=False,
)
# Рейс город вылета
FLIGHT_DEPARTURE_CITY = OpenApiParameter(
    name="departure_city",
    type=str,
    description="Город вылета",
    required=False,
)
# Рейс дата вылета
FLIGHT_DEPARTURE_DATE = OpenApiParameter(
    name="departure_date",
    type=str,
    description="Дата вылета",
    required=False,
)
# Рейс страна вылета
FLIGHT_ARRIVAL_COUNTRY = OpenApiParameter(
    name="arrival_country",
    type=str,
    description="Страна прилёта",
    required=False,
)
# Рейс город вылета
FLIGHT_ARRIVAL_CITY = OpenApiParameter(
    name="arrival_city",
    type=str,
    description="Город прилёта",
    required=False,
)
# Рейс дата вылета
FLIGHT_ARRIVAL_DATE = OpenApiParameter(
    name="arrival_date",
    type=str,
    description="Дата прилёта",
    required=False,
)
# Рейс номер
FLIGHT_NUMBER = OpenApiParameter(
    name="flight_number",
    type=str,
    description="Номер рейса",
    required=False,
)
# Для пагинации
LIMIT = OpenApiParameter(
    name="limit",
    type=int,
    description="Количество объектов на одной странице",
    required=False,
)
OFFSET = OpenApiParameter(
    name="offset",
    type=int,
    description="Начальный индекс для пагинации",
    required=False,
)
# ID статьи
ARTICLE_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID статьи",
    required=True,
)

# Лимит статей
ARTICLE_LIMIT = OpenApiParameter(
    name="limit",
    type=int,
    description="Количество статей на странице",
    required=False,
)

# Смещение
ARTICLE_OFFSET = OpenApiParameter(
    name="offset",
    type=int,
    description="Смещение от начала списка",
    required=False,
)

# Дата от
ARTICLE_DATE_FROM = OpenApiParameter(
    name="date_from",
    type=str,
    description="Дата публикации от (YYYY-MM-DD)",
    required=False,
)

# Дата до
ARTICLE_DATE_TO = OpenApiParameter(
    name="date_to",
    type=str,
    description="Дата публикации до (YYYY-MM-DD)",
    required=False,
)

# Сортировка
ARTICLE_POPULARITY = OpenApiParameter(
    name="popularity",
    type=str,
    description="Сортировка по популярности (asc/desc)",
    enum=["asc", "desc"],
    required=False,
)

# Страна
ARTICLE_COUNTRY = OpenApiParameter(
    name="country",
    type=str,
    description="Страна (русское название)",
    required=False,
)

# ID темы
ARTICLE_THEME_ID = OpenApiParameter(
    name="theme_id",
    type=int,
    description="ID темы статьи",
    required=False,
)

# Медиа статьи - ID
ARTICLE_MEDIA_ID = OpenApiParameter(
    location=OpenApiParameter.PATH,
    name="id",
    type=int,
    description="ID медиафайла статьи",
    required=True,
)

# Тип медиа (photo/video)
MEDIA_TYPE = OpenApiParameter(
    name="media_type",
    type=str,
    enum=["photo", "video"],
    description="Тип медиа: 'photo' или 'video'",
    required=False,
)

# Фото является обложкой
IS_COVER = OpenApiParameter(
    name="is_cover",
    type=bool,
    description="Является ли фото обложкой статьи (true/false)",
    required=False,
)

# Максимальное количество фото
MAX_PHOTOS_PARAM = OpenApiParameter(
    name="max_photos",
    type=int,
    description=f"Максимальное количество фото на статью ({MAX_PHOTOS})",
    required=False,
)

# Максимальное количество видео
MAX_VIDEOS_PARAM = OpenApiParameter(
    name="max_videos",
    type=int,
    description=f"Максимальное количество видео на статью ({MAX_VIDEOS})",
    required=False,
)

# Размер фото (MB)
PHOTO_SIZE = OpenApiParameter(
    name="photo_size",
    type=int,
    description=f"Максимальный размер фото в MB ({MAX_PHOTO_SIZE_MB})",
    required=False,
)

# Размер видео (MB)
VIDEO_SIZE = OpenApiParameter(
    name="video_size",
    type=int,
    description=f"Максимальный размер видео в MB ({MAX_VIDEO_SIZE_MB})",
    required=False,
)

# Длительность видео (секунды)
VIDEO_DURATION = OpenApiParameter(
    name="video_duration",
    type=int,
    description=f"Максимальная длительность видео в секундах ({MAX_VIDEO_DURATION})",
    required=False,
)

WARM_COUNTRIES = [
    "Египет",
    "Египет",
    "Марокко",
    "Тунис",
    "ЮАР",
    "Сейшельские острова",
    "Маврикий",
    "Кения",
    "Танзания",
    "Таиланд",
    "Мальдивы",
    "Индонезия",
    "Филиппины",
    "Вьетнам",
    "Малайзия",
    "Шри-Ланка",
    "ОАЭ",
    "Израиль",
    "Индия",
    "Испания",
    "Греция",
    "Италия",
    "Португалия",
    "Хорватия",
    "Турция",
    "Кипр",
    "Мальта",
    "Мексика",
    "Ямайка",
    "Доминиканская Республика",
    "Багамы",
    "Куба",
    "Коста-Рика",
    "Бразилия",
    "Аргентина",
    "Уругвай",
    "Колумбия",
    "Эквадор",
    "Австралия",
    "Фиджи",
    "Папуа-Новая Гвинея",
    "Самоа",
    "Тонга",
]

WARM_CITY = [
    # Африка
    "Шарм-эль-Шейх",
    "Хургада",
    "Александрия",
    "Марса-Алам",  # Египет
    "Агадир",
    "Эс-Сувейра",
    "Танжер",  # Марокко
    "Сусс",
    "Хаммамет",
    "Джерба",
    "Монастир",  # Тунис
    "Кейптаун",
    "Дурбан",  # ЮАР
    "Виктория",  # Сейшельские острова
    "Порт-Луи",  # Маврикий
    "Момбаса",
    "Малинди",  # Кения
    "Занзибар",
    "Дар-эс-Салам",  # Танзания
    # Азия
    "Пхукет",
    "Паттайя",
    "Самуи",
    "Краби",  # Таиланд
    "Мале",  # Мальдивы
    "Бали",
    "Ломбок",
    "Джакарта",  # Индонезия
    "Манила",
    "Себу",
    "Палаван",  # Филиппины
    "Нячанг",
    "Фантьет",
    "Да Нанг",
    "Хойан",  # Вьетнам
    "Куала-Лумпур",
    "Пенанг",
    "Лангкави",  # Малайзия
    "Коломбо",
    "Галле",
    "Тринкомали",  # Шри-Ланка
    "Дубай",
    "Абу-Даби",
    "Рас-эль-Хайма",  # ОАЭ
    "Тель-Авив",
    "Эйлат",  # Израиль
    "Панаджи",
    "Мумбаи",
    "Кочин",  # Индия
    # Европа
    "Барселона",
    "Малага",
    "Ибица",
    "Тенерифе",  # Испания
    "Афины",
    "Санторини",
    "Родос",
    "Крит",  # Греция
    "Неаполь",
    "Палермо",
    "Кальяри",
    "Римини",  # Италия
    "Лиссабон",
    "Алгарве",  # Португалия
    "Дубровник",
    "Сплит",
    "Пула",  # Хорватия
    "Анталья",
    "Аланья",
    "Бодрум",
    "Измир",
    "Сиде",  # Турция
    "Лимассол",
    "Пафос",  # Кипр
    "Валлетта",
    "Слима",  # Мальта
    # Карибский бассейн и Центральная Америка
    "Канкун",
    "Пуэрто-Вальярта",
    "Акапулько",
    "Тулум",  # Мексика
    "Монтего-Бей",
    "Оча-Риос",  # Ямайка
    "Пунта-Кана",
    "Ла-Романа",  # Доминиканская Республика
    "Нассау",  # Багамы
    "Варадеро",
    "Гавана",  # Куба
    "Сан-Хосе",
    "Тамариндо",  # Коста-Рика
    # Южная Америка
    "Рио-де-Жанейро",
    "Сан-Паулу",
    "Форталеза",
    "Натал",  # Бразилия
    "Мар-дель-Плата",  # Аргентина
    "Пунта-дель-Эсте",  # Уругвай
    "Картахена",
    "Санта-Марта",  # Колумбия
    "Гуаякиль",  # Эквадор
    # Океания
    "Сидней",
    "Голд-Кост",  # Австралия
    "Сува",  # Фиджи
    "Порт-Морсби",  # Папуа-Новая Гвинея
    "Апиа",  # Самоа
    "Нукуалофа",  # Тонга
]
DISCOUNT = (
    "Введите размер скидки, где 0.01 - это 1%, 1.00 - это 100%, а всё что больше 1.00 - это уже величина. "
    "Например 0.53 - это 53%, а 2000 - это величина скидки в виде 2000 рублей."
)


# ─── Параметры для Blog API ──────────────────────────────────────────────────
PUBLISHED_AT_AFTER = OpenApiParameter(
    name="published_at_after",
    location=OpenApiParameter.QUERY,
    description="Статьи, опубликованные начиная с указанной даты (YYYY-MM-DD)",
    required=False,
    type=OpenApiTypes.DATE,
)
PUBLISHED_AT_BEFORE = OpenApiParameter(
    name="published_at_before",
    location=OpenApiParameter.QUERY,
    description="Статьи, опубликованные не позднее указанной даты (YYYY-MM-DD)",
    required=False,
    type=OpenApiTypes.DATE,
)
COUNTRY = OpenApiParameter(
    name="country",
    location=OpenApiParameter.QUERY,
    description="Список русских названий стран",
    required=False,
    type=OpenApiTypes.STR,
    enum=[name for _, name in CountryChoices.choices],
)
THEME_ID = OpenApiParameter(
    name="theme_id",
    location=OpenApiParameter.QUERY,
    description="ID темы статьи",
    required=False,
    type=int,
)
ORDERING = OpenApiParameter(
    name="ordering",
    location=OpenApiParameter.QUERY,
    description="Поле для сортировки статей по необходимому параметру: тире перед именем поля => означает убывание",
    required=False,
    type=str,
    enum=[
        "published_at",
        "-published_at",
        "created_at",
        "-created_at",
        "views_count",
        "-views_count",
        "rating",
        "-rating",
    ],
)
SEARCH = OpenApiParameter(
    name="search",
    location=OpenApiParameter.QUERY,
    description="Текстовый поиск по заголовку и содержимому статьи",
    required=False,
    type=str,
)
# path-параметры
ARTICLE_ID = OpenApiParameter(
    name="id",
    location=OpenApiParameter.PATH,
    description="ID статьи",
    required=True,
)
CATEGORY_ID = OpenApiParameter(
    name="id",
    location=OpenApiParameter.PATH,
    description="ID категории",
    required=True,
)
TAG_ID = OpenApiParameter(
    name="id",
    location=OpenApiParameter.PATH,
    description="ID тега",
    required=True,
)
COMMENT_ID = OpenApiParameter(
    name="id",
    location=OpenApiParameter.PATH,
    description="ID комментария",
    required=True,
)
LIKE_ID = OpenApiParameter(
    name="id",
    location=OpenApiParameter.PATH,
    description="ID реакции",
    required=True,
)
COMMENT_Q = OpenApiParameter(
    name="comment",
    location=OpenApiParameter.QUERY,
    description="Фильтр по комментарию (ID)",
    required=False,
)

MIN_RATING = 0
MAX_RATING = 10
MIN_STARS = 0
MAX_STARS = 5
MIN_GUESTS = 1
MAX_GUESTS = 20
MIN_PRICE = 0
MAX_PRICE = 10000000
MAX_DAYS = 365
MIN_NIGHTS = 1
MAX_NIGHTS = 20
MIN_ADULT = 1
MAX_ADULT_CHILDREN = 19
MIN_CHILDREN = 0
