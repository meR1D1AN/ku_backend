from all_fixture.errors.list_error import DATE_ERROR

DATE_FIELD_SETTINGS = {
    "format": "%Y-%m-%d",
    "input_formats": ["%Y-%m-%d"],
    "error_messages": {"invalid": DATE_ERROR},
}

# Константа для полей
TOUR_FIELDS = (
    "id",
    "start_date",
    "end_date",
    "flight_to",
    "flight_from",
    "departure_country",
    "departure_city",
    "arrival_country",
    "arrival_city",
    "tour_operator",
    "hotel",
    "rooms",
    "type_of_meals",
    "transfer",
    "discount_amount",
    "discount_start_date",
    "discount_end_date",
    "markup_amount",
    "publish_start_date",
    "publish_end_date",
    "total_price",
    "created_at",
    "updated_at",
    "is_active",
)
