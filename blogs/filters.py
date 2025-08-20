from django.db import models
from django_filters import (
    CharFilter,
    DateFromToRangeFilter,
    FilterSet,
    NumberFilter,
)
from rest_framework.exceptions import ValidationError

from all_fixture.choices import CountryChoices
from blogs.models import Article, Theme


class ArticleFilter(FilterSet):
    """
    Набор фильтров для списка статей.

    Вместо двух DateFilter (date_from/date_to) используем единый DateFromToRangeFilter.
    Параметры запроса: `published_after` и/или `published_before` (YYYY-MM-DD).
    """

    published_at = DateFromToRangeFilter(
        field_name="published_at",
        method="filter_published",
        label="Диапазон публикации (ГГГГ-ММ-ДД)",
        help_text="Используйте параметры `published_after` и/или `published_before` в формате YYYY-MM-DD",
    )

    country = CharFilter(
        method="filter_country",
        label="Страны (русские названия)",
        help_text="CSV-список русских названий стран",
    )

    theme_id = NumberFilter(
        field_name="theme",
        method="filter_theme",
        label="ID темы",
        help_text="Фильтр по ID темы",
    )

    class Meta:
        model = Article
        fields: list[str] = []

    # ─────────────────────────── Дата публикации ────────────────────────────

    def filter_published(self, queryset, name, value):  # noqa: ARG002
        """
        Фильтр по диапазону дат публикации.

        Поддерживает одну или обе границы. Для DateTimeField используем `__date`,
        чтобы верхняя граница включала весь день.
        """
        start = getattr(value, "start", None)
        stop = getattr(value, "stop", None)

        # Валидация диапазона
        try:
            if start and stop and stop < start:
                raise ValidationError({"published": "Дата 'до' должна быть позже даты 'от'."})
        except TypeError as e:
            # Неизвестный/неверный формат значения
            raise ValidationError({"published": "Неверный формат дат. Используйте YYYY-MM-DD."}) from e

        # Определяем тип поля, чтобы правильно применить лукапы
        field = Article._meta.get_field("published_at")
        is_dt = isinstance(field, models.DateTimeField)

        if start and stop:
            lookup = "published_at__date__range" if is_dt else "published_at__range"
            return queryset.filter(**{lookup: (start, stop)})
        if start:
            lookup = "published_at__date__gte" if is_dt else "published_at__gte"
            return queryset.filter(**{lookup: start})
        if stop:
            lookup = "published_at__date__lte" if is_dt else "published_at__lte"
            return queryset.filter(**{lookup: stop})
        return queryset

        # ────────────────────────── Популярность / просмотры ─────────────────────
        """
    # Если понадобится отдельный фильтр, можно задействовать этот метод с ChoiceFilter.
    # Сейчас сортировка по просмотрам на OrderingFilter, что логично.
    # Но если вдруг, то вот функция.
    def filter_popularity(queryset, name, value):  # noqa: ARG003
        if value == "asc":
            return queryset.order_by("views_count")
        if value == "desc":
            return queryset.order_by("-views_count")
        raise ValidationError({"popularity": "Значение должно быть 'asc' или 'desc'."})
        """

    # ─────────────────────────────── Страна ──────────────────────────────────
    @staticmethod
    def filter_country(queryset, name, value):  # noqa: ARG003
        name_to_code = {ru_name: code for code, ru_name in CountryChoices.choices}
        codes, unknown = [], []
        for raw in str(value).split(","):
            ru = raw.strip()
            if not ru:
                continue
            code = name_to_code.get(ru)
            if code:
                codes.append(code)
            else:
                unknown.append(ru)
        if unknown:
            raise ValidationError({"country": f"Неизвестные страны: {', '.join(unknown)}"})
        if not codes:
            return queryset
        return queryset.filter(countries__contains=codes)

    # ─────────────────────────────── Тема ────────────────────────────────────

    def filter_theme(self, queryset, name, value):  # noqa: ARG003
        if not Theme.objects.filter(id=value).exists():
            raise ValidationError({"theme_id": "Тема с указанным ID не найдена."})
        return queryset.filter(theme_id=value)

    # ─────────────────────────── Права доступа ──────────────────────────────

    @property
    def qs(self):
        """
        анонимы — только published+moderated,
        авторы — свои черновики + published,
        суперпользователь — все.
        """
        base = super().qs
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return base.filter(is_published=True, is_moderated=True)
        if user.is_superuser:
            return base
        return base.filter(models.Q(is_published=True, is_moderated=True) | models.Q(author=user))
