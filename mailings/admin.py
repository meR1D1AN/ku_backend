from django.contrib import admin

from mailings.models import Mailing


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "mailing",
        "get_mailing_status",  # Красивое отображение статуса подписки
    )
    list_filter = ("mailing",)
    search_fields = ("email",)
    list_editable = ("mailing",)  # Позволяет редактировать mailing прямо из списка
    list_per_page = 20  # Количество элементов на странице

    @admin.display(description="Статус подписки", boolean=True)
    def get_mailing_status(self, obj):
        return obj.mailing

    actions = ["activate_mailing", "deactivate_mailing"]

    @admin.action(description="Активировать рассылку для выбранных")
    def activate_mailing(self, request, queryset):
        queryset.update(mailing=True)

    @admin.action(description="Деактивировать рассылку для выбранных")
    def deactivate_mailing(self, request, queryset):
        queryset.update(mailing=False)
