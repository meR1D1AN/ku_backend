from django.contrib import admin
from django.utils.html import format_html

from vzhuhs.forms import VzhuhForm
from vzhuhs.models import Vzhuh, VzhuhPhoto


@admin.register(VzhuhPhoto)
class VzhuhPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "photo_preview", "get_vzhuhs")
    list_display_links = ("id", "photo_preview")
    readonly_fields = ("get_vzhuhs",)

    def photo_preview(self, obj):
        if obj.photos:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.photos.url)
        return "Нет фото"

    photo_preview.short_description = "Превью фото"

    def get_vzhuhs(self, obj):
        return ", ".join([str(vzhuh) for vzhuh in obj.vzhuhs.all()])

    get_vzhuhs.short_description = "Связанные Вжухи"


@admin.register(Vzhuh)
class VzhuhAdmin(admin.ModelAdmin):
    form = VzhuhForm
    list_display = (
        "display_route",
        "departure_city",
        "arrival_city",
        "is_published",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_published", "departure_city", "arrival_city")
    search_fields = ("departure_city", "arrival_city", "description")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 30
    list_max_show_all = 300
    ordering = ("-created_at",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "departure_city",
                    "arrival_city",
                    "description",
                    "best_time_to_travel",
                    "suitable_for_whom",
                    "photos",
                )
            },
        ),
        ("Туры", {"fields": ("tours",)}),
        ("Отели", {"fields": ("hotels", "description_hotel")}),
        ("Блог", {"fields": ("description_blog",)}),
        (
            "Системные",
            {
                "fields": (
                    "is_published",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    actions = (
        "publish_vzhuhs",
        "unpublish_vzhuhs",
    )

    def display_route(self, obj):
        """
        Отображает маршрут в списке.
        """
        return obj.route

    display_route.short_description = "Маршрут"

    @admin.action(description="Опубликовать выбранные Вжухи")
    def publish_vzhuhs(self, request, queryset):
        """Массовая публикация Вжухов."""
        queryset.update(is_published=True)

    @admin.action(description="Снять с публикации выбранные Вжухи")
    def unpublish_vzhuhs(self, request, queryset):
        """Массовое снятие Вжухов с публикации."""
        queryset.update(is_published=False)
