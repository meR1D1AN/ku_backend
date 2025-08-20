from django.contrib import admin

from guests.models import Guest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    """
    Админ панель для модели Guest
    """

    list_display = ("pk", "firstname", "lastname", "surname", "date_born", "user_owner")
    search_fields = ("firstname", "lastname", "surname")
