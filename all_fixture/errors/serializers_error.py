from rest_framework.serializers import CharField, ListField, Serializer

from all_fixture.errors.list_error import (
    APPLICATION_HOTEL_ERROR,
    APPLICATION_TOUR_ERROR,
    FLIGHT_ERROR,
    FLIGHT_FROM_ERROR,
    FLIGHT_TO_ERROR,
    GUEST_AUTH_ERROR,
    GUEST_ERROR,
    GUEST_USER_ERROR,
    HOTEL_FORMAT_ERROR,
    HOTEL_ID_ERROR,
    INSURANCE_ERROR,
    PHOTO_ERROR,
    PHOTO_FILE_ERROR,
    ROOM_DATE_ERROR,
    ROOM_FORMAT_ERROR,
    ROOM_ID_ERROR,
    TOUR_ERROR,
    TOUROPERATOR_ERROR,
    TOUROPERATOR_FORMAT_ERROR,
    TYPE_OF_MEAL_ERROR,
    TYPE_OF_MEAL_FORMAT_ERROR,
    TYPE_OF_MEAL_NAME_ERROR,
)

FLIGHT_TO_ERROR_MESSAGES = {
    "does_not_exist": FLIGHT_ERROR,
    "invalid": FLIGHT_TO_ERROR,
}
FLIGHT_FROM_ERROR_MESSAGES = {
    "does_not_exist": FLIGHT_ERROR,
    "invalid": FLIGHT_FROM_ERROR,
}
TOUROPERATOR_ERROR_MESSAGES = {
    "does_not_exist": TOUROPERATOR_ERROR,
    "invalid": TOUROPERATOR_FORMAT_ERROR,
}
HOTEL_ERROR_MESSAGES = {
    "does_not_exist": HOTEL_ID_ERROR,
    "invalid": HOTEL_FORMAT_ERROR,
}
ROOMS_ERROR_MESSAGES = {
    "does_not_exist": ROOM_ID_ERROR,
    "invalid": ROOM_FORMAT_ERROR,
    "null": "Список номеров не может быть пустым.",
    "blank": "Список номеров не может быть пустым.",
    "not_a_list": "Ожидается список ID номеров.",
}
TYPE_OF_MEALS_ERROR_MESSAGES = {
    "does_not_exist": TYPE_OF_MEAL_ERROR,
    "invalid": TYPE_OF_MEAL_FORMAT_ERROR,
    "null": "Список типов питания не может быть пустым.",
    "blank": "Список типов питания не может быть пустым.",
    "not_a_list": "Ожидается список ID типов питания.",
}


class MailingErrorSerializer(Serializer):
    detail = CharField()


class ApplicationHotelErrorIdSerializer(Serializer):
    detail = CharField(default=APPLICATION_HOTEL_ERROR)


class ApplicationTourErrorIdSerializer(Serializer):
    detail = CharField(default=APPLICATION_TOUR_ERROR)


class FlightErrorIdSerializer(Serializer):
    detail = CharField(default=FLIGHT_ERROR)


class GuestErrorBaseSerializer(Serializer):
    detail = CharField()


class GuestErrorIdSerializer(Serializer):
    detail = CharField(default=GUEST_ERROR)


class GuestErrorAuthSerializer(Serializer):
    detail = CharField(default=GUEST_AUTH_ERROR)


class GuestErrorUserSerializer(Serializer):
    detail = CharField(default=GUEST_USER_ERROR)


class InsurancesErrorIdSerializer(Serializer):
    detail = CharField(default=INSURANCE_ERROR)


class TourErrorBaseSerializer(Serializer):
    detail = CharField()


class TourErrorSerializer(Serializer):
    detail = CharField(default=TOUR_ERROR)


class RoomBaseEroorSerializer(Serializer):
    detail = CharField()


class RoomErrorIdSerializer(Serializer):
    detail = CharField(default=ROOM_ID_ERROR)


class RoomPhotoErrorIdSerializer(Serializer):
    detail = CharField(default=PHOTO_ERROR)


class RoomPhotoErrorFileSerializer(Serializer):
    photo = ListField(child=CharField(), default=[PHOTO_FILE_ERROR])


class RoomDateErrorBaseSerializer(Serializer):
    detail = CharField()


class RoomDateErrorHotelIdSerializer(Serializer):
    detail = CharField(default=HOTEL_ID_ERROR)


class RoomDateErrorSerializer(Serializer):
    detail = CharField(default=ROOM_DATE_ERROR)


class HotelBaseErrorSerializer(Serializer):
    detail = CharField()


class HotelErrorIdSerializer(Serializer):
    detail = CharField(default=HOTEL_ID_ERROR)


class HotelPhotoErrorBaseSerializer(Serializer):
    detail = CharField()


class HotelPhotoErrorIdSerializer(Serializer):
    detail = CharField(default=PHOTO_ERROR)


class HotelPhotoErrorFileSerializer(Serializer):
    photo = ListField(child=CharField(), default=[PHOTO_FILE_ERROR])


class TypeOfMealErrorBaseSerializer(Serializer):
    detail = CharField()


class TypeOfMealErrorIdSerializer(Serializer):
    detail = CharField(default=TYPE_OF_MEAL_ERROR)


class TypeOfMealErrorNameSerializer(Serializer):
    detail = CharField(default=TYPE_OF_MEAL_NAME_ERROR)
