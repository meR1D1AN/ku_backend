from django.contrib import admin

from rooms.models import Room, RoomPhoto, RoomRules


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "hotel",
        "number_of_adults",
    )
    list_display_links = ("id",)
    search_fields = ("id",)


@admin.register(RoomPhoto)
class RoomPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "photo")


@admin.register(RoomRules)
class RoomRulesAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "option")
    exclude = ("created_by",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
