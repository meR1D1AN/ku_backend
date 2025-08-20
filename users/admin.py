from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


# ─────────── Массовые действия ────────────────────────────────────────────
@admin.action(description="Деактивировать выбранных пользователей")
def admin_deactivate(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.action(description="Реактивировать выбранных пользователей")
def admin_reactivate(modeladmin, request, queryset):
    queryset.update(is_active=True, ban_until=None, ban_level=0, failed_login_count=0)


# ─────────── Admin class ─────────────────────────────────────────────
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка для управления пользователями, с группами."""

    # Полностью убираем username на формах создания
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    # ---------- отображение списка ----------
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "ban_until",
        "failed_login_count",
        "ban_level",
    )
    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
        "ban_level",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)

    # ---------- поля «только чтение» ----------
    readonly_fields = (
        "last_login",
        "date_joined",
        "ban_until",
        "failed_login_count",
        "ban_level",
    )

    # ---------- формы редактирования ----------
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name", "phone_number", "avatar", "birth_date")}),
        ("Роли и права", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups")}),
        (
            "Безопасность входа",
            {  # ← добавили секцию банов
                "fields": ("failed_login_count", "ban_level", "ban_until"),
                "description": "Автоблокировка после 5 неудачных логинов",
            },
        ),
        ("Компания", {"fields": ("company_name", "documents")}),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )

    # ---------- горизонтальные связи ----------
    filter_horizontal = ("groups",)

    # ---------- массовые действия ----------
    actions = [admin_deactivate, admin_reactivate]

    # ---------- фильтрация видимости ----------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.groups.filter(name="Admin").exists():
            return qs.exclude(role="Super Admin")
        if request.user.groups.filter(name="Tour Operators").exists():
            return qs.filter(role="TOUR_OPERATOR")
        if request.user.groups.filter(name="Hoteliers").exists():
            return qs.filter(role="HOTELIER")
        return qs.none()
