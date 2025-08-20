from django.db import models


class MedicalInsuranceChoices(models.TextChoices):
    """
    Выбор страховых компаний
    """

    TSINSURANCE = "Т-Страхование", "Т-Страхование"
    SOVCOMINSURANCE = "Совкомбанк Страхование", "Совкомбанк Страхование"
    SBERINSURANCE = "Сбербанк Страхование", "Сбербанк Страхование"
    VSKINSURANCE = "ВСК Страхование", "ВСК Страхование"
    ROSGORINSURANCE = "Росгорстрах", "Росгорстрах"
    RESOINSURANCE = "РЕСО Страхование", "РЕСО Страхование"
    SOGLASIEINSURANCE = "Согласие", "Согласие"
    SOGAZINSURANCE = "СОГАЗ", "СОГАЗ"
    ALFAINSURANCE = "Альфа Страхование", "Альфа Страхование"
    RENESSANSINSURANCE = "Ренессанс Страхование", "Ренессанс Страхование"
    INGOSTRAHINSURANCE = "Ингострах", "Ингострах"
    INTOUCHINSURANCE = "INTOUCH", "INTOUCH"
    NOTSELECTED = "Не выбрано", "Не выбрано"


class NotLeavingInsuranceChoices(models.TextChoices):
    """
    Выбор страховых компаний
    """

    SOGAZINSURANCE = "СОГАЗ", "СОГАЗ"
    TSINSURANCE = "Т-Страхование", "Т-Страхование"
    SOVCOMINSURANCE = "Совкомбанк Страхование", "Совкомбанк Страхование"
    SBERINSURANCE = "Сбербанк Страхование", "Сбербанк Страхование"
    VSKINSURANCE = "ВСК Страхование", "ВСК Страхование"
    ROSGORINSURANCE = "Росгорстрах", "Росгорстрах"
    RESOINSURANCE = "РЕСО Страхование", "РЕСО Страхование"
    SOGLASIEINSURANCE = "Согласие", "Согласие"
    ALFAINSURANCE = "Альфа Страхование", "Альфа Страхование"
    RENESSANSINSURANCE = "Ренессанс Страхование", "Ренессанс Страхование"
    INGOSTRAHINSURANCE = "Ингострах", "Ингострах"
    INTOUCHINSURANCE = "INTOUCH", "INTOUCH"
    NOTSELECTED = "Не выбрано", "Не выбрано"


class PlaceChoices(models.TextChoices):
    """
    Выбор типом размещения
    """

    HOTEL = "Отель", "Отель"
    HOSTEL = "Хостел", "Хостел"
    VILLA = "Вилла", "Вилла"
    APARTMENT = "Апартаменты", "Апартаменты"
    GUEST_HOUSE = "Гостевой дом", "Гостевой дом"
    INN = "Гостиница", "Гостиница"


class TypeOfHolidayChoices(models.TextChoices):
    """
    Выбор типов отдыха
    """

    BEACH = "Пляжный", "Пляжный"
    CITY = "Городской", "Городской"
    SPA = "Спа", "Спа"
    HEALING = "Лечебный", "Лечебный"
    WITH_CHILDREN = "С детьми", "С детьми"
    WITH_ANIMALS = "С животными", "С животными"


class CurrencyChoices(models.TextChoices):
    """Валюты, используемые пользователем."""

    RUB = "RUB", "Рубль"
    EUR = "EUR", "Евро"
    USD = "USD", "Доллар"


class LanguageChoices(models.TextChoices):
    """Языки интерфейса, доступные пользователем."""

    RU = "RU", "Русский"
    EN = "EN", "Английский"


class ContactPriorityChoices(models.TextChoices):
    """Предпочтительный канал связи с пользователем."""

    PHONE = "phone", "Телефон"
    EMAIL = "email", "Email"


class WhatAboutChoices(models.TextChoices):
    """
    Выбор подборок для Что насчёт...
    """

    EXPLORE_THE_STREETS = (
        "Что насчёт поисследовать улочки в Италии",
        "Что насчёт поисследовать улочки в Италии",
    )
    ALL_WEEKEND = (
        "Что насчёт на все выходные в Санкт-Петербурге",
        "Что насчёт на все выходные в Санкт-Петербурге",
    )
    EXPLORE_THE_ASIA = (
        "Что насчёт исследовать китайскую культуру в Шанхае",
        "Что насчёт исследовать китайскую культуру в Шанхае",
    )
    RELAX_ON_THE_ISLAND = (
        "Что насчёт расслабиться на островах Таиланда",
        "Что насчёт расслабиться на островах Таиланда",
    )
    WARM = "Что насчёт погреться в Турции", "Что насчёт погреться в Турции"


class AirlinesChoices(models.TextChoices):
    """
    Авиакомпания
    """

    AEROFLOT = "Аэрофлот", "Аэрофлот"
    POBEDA = "Победа", "Победа"
    ROSSIA = "Россия", "Россия"
    S7 = "S7", "S7"
    URAL_AIRLINES = "Уральские авиалинии", "Уральские авиалинии"
    NORDWIND = "Северный ветер", "Северный ветер"
    TURKISH_AIRLINES = "Turkish airlines", "Turkish airlines"
    EMIRATES = "Emirates", "Emirates"
    AZIMUT = "Азимут", "Азимут"
    RED_WINGS = "Red Wings", "Red Wings"
    UTAIR = "UTair", "UTair"
    YAMAL = "Ямал", "Ямал"
    PEGASUS = "Pegasus Airlines", "Pegasus Airlines"
    AZUR = "Azur Air", "Azur Air"
    CORENDON = "Corendon Airlines", "Corendon Airlines"
    AIR_ARADIA = "Air Arabia", "Air Arabia"
    FLY_DYDAI = "Fly Dubai", "Fly Dubai"
    CHINA_S = "China Southern Airlines", "China Southern Airlines"
    CHINA_E = "China Eastern", "China Eastern"
    SICHUAN = "Sichuan Airlines", "Sichuan Airlines"
    QATAR = "Qatar Airways", "Qatar Airways"
    BELAVIA = "Белавиа", "Белавиа"


class ServicesClassChoices(models.TextChoices):
    """
    Класс обслуживания
    """

    ECONOMY = "Эконом", "Эконом"
    BUSINESS = "Бизнес", "Бизнес"
    FIRST = "Первый", "Первый"


class FlightTypeChoices(models.TextChoices):
    """
    Тип рейса
    """

    REGULAR = "Регулярный", "Регулярный"
    CHARTER = "Чартерный", "Чартерный"
    TRANZIT = "Транзитный", "Транзитный"


class RoomCategoryChoices(models.TextChoices):
    """
    Категория номера
    """

    STANDARD = "Standard", "Standard"
    SINGLE_ROOM = "Single Room", "Single Room"
    DOUBLE_ROOM = "Double Room", "Double Room"
    TWIN_ROOM = "Twin Room", "Twin Room"
    TRIPLE_ROOM = "Triple Room", "Triple Room"
    FAMILY_ROOM = "Family Room", "Family Room"
    SUPERIOR_ROOM = "Superior Room", "Superior Room"
    DELUXE_ROOM = "Deluxe Room", "Deluxe Room"
    STUDIO = "Studio", "Studio"
    SUITE = "Suite", "Suite"
    JUNIOR_SUITE = "Junior Suite", "Junior Suite"
    RESIDENCE = "Residence", "Residence"
    ROYAL_SUITE = "Royal Suite", "Royal Suite"
    PENTHOUSE = "Penthouse", "Penthouse"


class TypeOfMealChoices(models.TextChoices):
    """
    Тип питания
    """

    NO_MEAL = "Без питания", "Без питания"
    BREAKFAST = "Завтрак", "Завтрак"
    BREAKFAST_AND_DINNER = "Завтрак и ужин", "Завтрак и ужин"
    FULL_BOARD = "Полный пансион", "Полный пансион"
    ALL_INCLUSIVE = "All inclusive", "All inclusive"
    ULTRA_ALL_INCLUSIVE = "Ultra all inclusive", "Ultra all inclusive"


class StatusChoices(models.TextChoices):
    """
    Выбор статуса для заявки
    """

    CONFIRM = "Подтвержден", "Подтвержден"
    AWAIT_CONFIRM = "Ожидает подтверждения", "Ожидает подтверждения"
    NEED_CONTACT = "Необходимо связаться", "Необходимо связаться"


class RoleChoices(models.TextChoices):
    """
    Выбор роли пользователя
    """

    USER = "USER", "Пользователь"
    TOUR_OPERATOR = "TOUR_OPERATOR", "Туроператор"
    HOTELIER = "HOTELIER", "Отельер"
    ADMIN = "ADMIN", "Администратор"


class CountryChoices(models.TextChoices):
    """
    Полный список стран по стандарту ISO 3166-1 с русскими названиями.
    """

    AF = "AF", "Афганистан"
    AX = "AX", "Аландские острова"
    AL = "AL", "Албания"
    DZ = "DZ", "Алжир"
    AS = "AS", "Американское Самоа"
    AD = "AD", "Андорра"
    AO = "AO", "Ангола"
    AI = "AI", "Ангилья"
    AQ = "AQ", "Антарктида"
    AG = "AG", "Антигуа и Барбуда"
    AR = "AR", "Аргентина"
    AM = "AM", "Армения"
    AW = "AW", "Аруба"
    AU = "AU", "Австралия"
    AT = "AT", "Австрия"
    AZ = "AZ", "Азербайджан"
    BS = "BS", "Багамы"
    BH = "BH", "Бахрейн"
    BD = "BD", "Бангладеш"
    BB = "BB", "Барбадос"
    BY = "BY", "Беларусь"
    BE = "BE", "Бельгия"
    BZ = "BZ", "Белиз"
    BJ = "BJ", "Бенин"
    BM = "BM", "Бермуды"
    BT = "BT", "Бутан"
    BO = "BO", "Боливия"
    BQ = "BQ", "Бонайре, Синт-Эстатиус и Саба"
    BA = "BA", "Босния и Герцеговина"
    BW = "BW", "Ботсвана"
    BV = "BV", "Остров Буве"
    BR = "BR", "Бразилия"
    IO = "IO", "Британская территория в Индийском океане"
    BN = "BN", "Бруней"
    BG = "BG", "Болгария"
    BF = "BF", "Буркина-Фасо"
    BI = "BI", "Бурунди"
    CV = "CV", "Кабо-Верде"
    KH = "KH", "Камбоджа"
    CM = "CM", "Камерун"
    CA = "CA", "Канада"
    KY = "KY", "Каймановы острова"
    CF = "CF", "ЦАР"
    TD = "TD", "Чад"
    CL = "CL", "Чили"
    CN = "CN", "Китай"
    CX = "CX", "Остров Рождества"
    CC = "CC", "Кокосовые острова"
    CO = "CO", "Колумбия"
    KM = "KM", "Коморы"
    CG = "CG", "Конго"
    CD = "CD", "ДР Конго"
    CK = "CK", "Острова Кука"
    CR = "CR", "Коста-Рика"
    CI = "CI", "Кот-д’Ивуар"
    HR = "HR", "Хорватия"
    CU = "CU", "Куба"
    CW = "CW", "Кюрасао"
    CY = "CY", "Кипр"
    CZ = "CZ", "Чехия"
    DK = "DK", "Дания"
    DJ = "DJ", "Джибути"
    DM = "DM", "Доминика"
    DO = "DO", "Доминикана"
    EC = "EC", "Эквадор"
    EG = "EG", "Египет"
    SV = "SV", "Сальвадор"
    GQ = "GQ", "Экваториальная Гвинея"
    ER = "ER", "Эритрея"
    EE = "EE", "Эстония"
    SZ = "SZ", "Эсватини"
    ET = "ET", "Эфиопия"
    FK = "FK", "Фолклендские острова"
    FO = "FO", "Фарерские острова"
    FJ = "FJ", "Фиджи"
    FI = "FI", "Финляндия"
    FR = "FR", "Франция"
    GF = "GF", "Французская Гвиана"
    PF = "PF", "Французская Полинезия"
    TF = "TF", "Французские Южные территории"
    GA = "GA", "Габон"
    GM = "GM", "Гамбия"
    GE = "GE", "Грузия"
    DE = "DE", "Германия"
    GH = "GH", "Гана"
    GI = "GI", "Гибралтар"
    GR = "GR", "Греция"
    GL = "GL", "Гренландия"
    GD = "GD", "Гренада"
    GP = "GP", "Гваделупа"
    GU = "GU", "Гуам"
    GT = "GT", "Гватемала"
    GG = "GG", "Гернси"
    GN = "GN", "Гвинея"
    GW = "GW", "Гвинея-Бисау"
    GY = "GY", "Гайана"
    HT = "HT", "Гаити"
    HM = "HM", "Острова Херд и Макдональд"
    VA = "VA", "Ватикан"
    HN = "HN", "Гондурас"
    HK = "HK", "Гонконг"
    HU = "HU", "Венгрия"
    IS = "IS", "Исландия"
    IN = "IN", "Индия"
    ID = "ID", "Индонезия"
    IR = "IR", "Иран"
    IQ = "IQ", "Ирак"
    IE = "IE", "Ирландия"
    IM = "IM", "Остров Мэн"
    IL = "IL", "Израиль"
    IT = "IT", "Италия"
    JM = "JM", "Ямайка"
    JP = "JP", "Япония"
    JE = "JE", "Джерси"
    JO = "JO", "Иордания"
    KZ = "KZ", "Казахстан"
    KE = "KE", "Кения"
    KI = "KI", "Кирибати"
    KP = "KP", "КНДР"
    KR = "KR", "Корея"
    KW = "KW", "Кувейт"
    KG = "KG", "Киргизия"
    LA = "LA", "Лаос"
    LV = "LV", "Латвия"
    LB = "LB", "Ливан"
    LS = "LS", "Лесото"
    LR = "LR", "Либерия"
    LY = "LY", "Ливия"
    LI = "LI", "Лихтенштейн"
    LT = "LT", "Литва"
    LU = "LU", "Люксембург"
    MO = "MO", "Макао"
    MG = "MG", "Мадагаскар"
    MW = "MW", "Малави"
    MY = "MY", "Малайзия"
    MV = "MV", "Мальдивы"
    ML = "ML", "Мали"
    MT = "MT", "Мальта"
    MH = "MH", "Маршалловы острова"
    MQ = "MQ", "Мартиника"
    MR = "MR", "Мавритания"
    MU = "MU", "Маврикий"
    YT = "YT", "Майотта"
    MX = "MX", "Мексика"
    FM = "FM", "Микронезия"
    MD = "MD", "Молдова"
    MC = "MC", "Монако"
    MN = "MN", "Монголия"
    ME = "ME", "Черногория"
    MS = "MS", "Монтсеррат"
    MA = "MA", "Марокко"
    MZ = "MZ", "Мозамбик"
    MM = "MM", "Мьянма"
    NA = "NA", "Намибия"
    NR = "NR", "Науру"
    NP = "NP", "Непал"
    NL = "NL", "Нидерланды"
    NC = "NC", "Новая Каледония"
    NZ = "NZ", "Новая Зеландия"
    NI = "NI", "Никарагуа"
    NE = "NE", "Нигер"
    NG = "NG", "Нигерия"
    NU = "NU", "Ниуэ"
    NF = "NF", "Остров Норфолк"
    MK = "MK", "Северная Македония"
    MP = "MP", "Северные Марианские острова"
    NO = "NO", "Норвегия"
    OM = "OM", "Оман"
    PK = "PK", "Пакистан"
    PW = "PW", "Палау"
    PS = "PS", "Палестина"
    PA = "PA", "Панама"
    PG = "PG", "Папуа — Новая Гвинея"
    PY = "PY", "Парагвай"
    PE = "PE", "Перу"
    PH = "PH", "Филиппины"
    PN = "PN", "Острова Питкэрн"
    PL = "PL", "Польша"
    PT = "PT", "Португалия"
    PR = "PR", "Пуэрто-Рико"
    QA = "QA", "Катар"
    RE = "RE", "Реюньон"
    RO = "RO", "Румыния"
    RU = "RU", "Россия"
    RW = "RW", "Руанда"
    BL = "BL", "Сен-Бартелеми"
    SH = "SH", "Остров Святой Елены"
    KN = "KN", "Сент-Китс и Невис"
    LC = "LC", "Сент-Люсия"
    MF = "MF", "Сен-Мартен"
    PM = "PM", "Сен-Пьер и Микелон"
    VC = "VC", "Сент-Винсент и Гренадины"
    WS = "WS", "Самоа"
    SM = "SM", "Сан-Марино"
    ST = "ST", "Сан-Томе и Принсипи"
    SA = "SA", "Саудовская Аравия"
    SN = "SN", "Сенегал"
    RS = "RS", "Сербия"
    SC = "SC", "Сейшелы"
    SL = "SL", "Сьерра-Леоне"
    SG = "SG", "Сингапур"
    SX = "SX", "Синт-Мартен"
    SK = "SK", "Словакия"
    SI = "SI", "Словения"
    SB = "SB", "Соломоновы острова"
    SO = "SO", "Сомали"
    ZA = "ZA", "ЮАР"
    GS = "GS", "Южная Георгия и Южные Сандвичевы острова"
    SS = "SS", "Южный Судан"
    ES = "ES", "Испания"
    LK = "LK", "Шри-Ланка"
    SD = "SD", "Судан"
    SR = "SR", "Суринам"
    SJ = "SJ", "Шпицберген и Ян-Майен"
    SE = "SE", "Швеция"
    CH = "CH", "Швейцария"
    SY = "SY", "Сирия"
    TW = "TW", "Тайвань"
    TJ = "TJ", "Таджикистан"
    TZ = "TZ", "Танзания"
    TH = "TH", "Таиланд"
    TL = "TL", "Тимор-Лесте"
    TG = "TG", "Того"
    TK = "TK", "Токелау"
    TO = "TO", "Тонга"
    TT = "TT", "Тринидад и Тобаго"
    TN = "TN", "Тунис"
    TR = "TR", "Турция"
    TM = "TM", "Туркменистан"
    TC = "TC", "Острова Тёркс и Кайкос"
    TV = "TV", "Тувалу"
    UG = "UG", "Уганда"
    UA = "UA", "Украина"
    AE = "AE", "ОАЭ"
    GB = "GB", "Великобритания"
    US = "US", "США"
    UM = "UM", "Малые Тихоокеанские отдаленные острова США"
    UY = "UY", "Уругвай"
    UZ = "UZ", "Узбекистан"
    VU = "VU", "Вануату"
    VE = "VE", "Венесуэла"
    VN = "VN", "Вьетнам"
    VG = "VG", "Британские Виргинские острова"
    VI = "VI", "Виргинские острова (США)"
    WF = "WF", "Уоллис и Футуна"
    EH = "EH", "САДР"
    YE = "YE", "Йемен"
    ZM = "ZM", "Замбия"
    ZW = "ZW", "Зимбабве"

    @classmethod
    def sorted_choices(cls):
        return sorted(cls.choices, key=lambda x: x[1])
