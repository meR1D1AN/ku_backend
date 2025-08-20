from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.utils.text import capfirst

from all_fixture.choices import CountryChoices
from blogs.models import (
    Article,
    Category,
    Comment,
    MediaAsset,
    Tag,
    Theme,
)

# ---- Базовый админ для справочников name/slug --------------------------------


class SlugNameAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(SlugNameAdmin):
    """Админка для категорий."""


@admin.register(Tag)
class TagAdmin(SlugNameAdmin):
    """Админка для тегов."""


@admin.register(Theme)
class ThemeAdmin(SlugNameAdmin):
    """Админка для тем."""


# ---- Фильтры -----------------------------------------------------------------


class CountryListFilter(admin.SimpleListFilter):
    title = "Страна"
    parameter_name = "country"

    def lookups(self, request, model_admin):
        # Полный справочник стран (красиво отсортированный), а не только "используемые"
        return CountryChoices.sorted_choices()

    def queryset(self, request, queryset):
        return queryset.filter(countries__contains=[self.value()]) if self.value() else queryset


class AuthorListFilter(admin.SimpleListFilter):
    title = "Автор"
    parameter_name = "author"

    # показывать фильтр даже если список пуст
    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        user_model = get_user_model()
        author_ids = model_admin.get_queryset(request).values_list("author_id", flat=True).distinct()

        # есть статьи -> авторы из статей
        if author_ids:
            users = user_model.objects.filter(id__in=author_ids)
        # статей нет -> подстраховка (иначе фильтр был бы пуст и скрыт)
        else:
            users = user_model.objects.filter(is_staff=True)

        users = users.order_by("last_name", "first_name", "email")[:50]

        def label(u):
            return u.get_full_name() or getattr(u, "email", None) or getattr(u, "phone_number", None) or f"ID {u.pk}"

        return [(u.pk, capfirst(label(u))) for u in users]

    def queryset(self, request, queryset):
        return queryset.filter(author_id=self.value()) if self.value() else queryset


class CommentAuthorListFilter(admin.SimpleListFilter):
    title = "Автор"
    parameter_name = "user"

    def has_output(self):
        # показывать фильтр даже если пока пусто
        return True

    def lookups(self, request, model_admin):
        user_model = get_user_model()
        user_ids = model_admin.get_queryset(request).values_list("user_id", flat=True).distinct()

        if user_ids:
            users = user_model.objects.filter(id__in=user_ids)
        else:
            # подстраховка для пустых данных
            users = user_model.objects.filter(is_staff=True)

        users = users.order_by("last_name", "first_name", "email")[:100]

        def label(u):
            # показываем ФИО; если его нет — email/телефон; без «tourists.<uuid>@…»
            return (
                (u.get_full_name() or "").strip()
                or getattr(u, "email", None)
                or getattr(u, "phone_number", None)
                or f"ID {u.pk}"
            )

        return [(u.pk, capfirst(label(u))) for u in users]

    def queryset(self, request, qs):
        return qs.filter(user_id=self.value()) if self.value() else qs


# ---- Article -----------------------------------------------------------------


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Админка для статей."""

    list_display = (
        "title",
        "author_display",
        "status",
        "views_count",
        "reading_time_minutes",
        "created_at",
        "updated_at",
        "display_countries",
    )
    list_filter = (
        "status",
        "category",
        "theme",
        CountryListFilter,
        AuthorListFilter,
        "created_at",
    )
    search_fields = ("title", "content", "countries")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("tags", "theme", "category")
    list_select_related = ("author", "category", "theme")
    prefetch_related = ("tags",)

    # удобный виджет для ArrayField стран
    formfield_overrides = {
        ArrayField: {
            "widget": forms.SelectMultiple(choices=CountryChoices.sorted_choices()),
        },
    }

    @admin.display(description="Страны")
    def display_countries(self, obj):
        mapping = dict(CountryChoices.choices)
        return ", ".join(mapping.get(code, code) for code in (obj.countries or []))

    @admin.display(description="Автор", ordering="author__last_name")
    def author_display(self, obj):
        u = obj.author
        return u.get_full_name() or getattr(u, "email", None) or getattr(u, "phone_number", None) or f"ID {u.pk}"


# ---- Комментарии -------------------------------------------------------------


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "article",
        "text",
        "user_display",
        "status",
        "likes_count_display",
        "dislikes_count_display",
        "created_at",
    )
    list_filter = ("status", "article", CommentAuthorListFilter, "created_at")
    search_fields = ("text", "user__email", "user__first_name", "user__last_name", "user__phone_number")
    list_select_related = ("article", "user")
    actions = ("approve_comments",)

    @admin.display(description="Автор", ordering="user__last_name")
    def user_display(self, obj):
        u = obj.user
        return (
            (u.get_full_name() or "").strip()
            or getattr(u, "email", None)
            or getattr(u, "phone_number", None)
            or f"ID {u.pk}"
        )

    @admin.display(description="Лайки")
    def likes_count_display(self, obj):
        # если есть аннотированное поле likes_count — используем его, иначе считаем
        return getattr(obj, "likes_count", obj.likes.filter(is_like=True).count())

    @admin.display(description="Дизлайки")
    def dislikes_count_display(self, obj):
        return getattr(obj, "dislikes_count", obj.likes.filter(is_like=False).count())

    # правильная сигнатура action: (self, request, queryset)
    def approve_comments(self, request, queryset):
        queryset.update(status="approved")

    approve_comments.short_description = "Одобрить выбранные комментарии"


# ---- Медиа -------------------------------------------------------------------


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("article", "type", "file", "order")
    list_filter = ("type", "article")
    search_fields = ("file",)
    list_select_related = ("article",)
