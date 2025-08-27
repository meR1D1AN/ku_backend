from django.contrib import admin

from hotels.models import Hotel, HotelPhoto, HotelRules, HotelWhatAbout, TypeOfMeal


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("id", "type_of_rest", "name", "country", "city", "address")
    list_display_links = ("id", "name")
    search_fields = ("id",)


@admin.register(HotelWhatAbout)
class HotelWhatAboutAdmin(admin.ModelAdmin):
    list_display = ("id", "name_set")


@admin.register(TypeOfMeal)
class TypeOfMealsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "hotel")


@admin.register(HotelPhoto)
class HotelPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "photo")


@admin.register(HotelRules)
class HotelRulesAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
