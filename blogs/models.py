from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from all_fixture.choices import CountryChoices
from all_fixture.views_fixture import NULLABLE
from blogs.constants import (
    ALLOWED_VIDEO_EXT,
    MAX_FILE_SIZE_BYTES,
)
from blogs.validators import enforce_media_limit, validate_media_file

USER_MODEL = settings.AUTH_USER_MODEL


# ──────────────────────────── валидаторы, завязанные на константы ────────────────────────────
def validate_file_size(file):
    """Общий чек размера (10 МБ)."""
    if file.size > MAX_FILE_SIZE_BYTES:
        raise ValidationError("Файл слишком большой (>10 МБ)")


def validate_video_ext(file):
    """Доп-проверка формата для видео."""
    if Path(file.name).suffix.lower() not in ALLOWED_VIDEO_EXT:
        raise ValidationError("Поддерживаются только MP4 и WebM")


# ───────────────────────────── название / slug mixin ─────────────────────────────
class SlugNameModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")

    class Meta:
        abstract = True
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:90]
            slug = base
            n = 1
            while self.__class__.objects.filter(slug=slug).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Category(SlugNameModel):
    class Meta(SlugNameModel.Meta):
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Tag(SlugNameModel):
    class Meta(SlugNameModel.Meta):
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Theme(SlugNameModel):
    class Meta(SlugNameModel.Meta):
        verbose_name = "Тема статьи"
        verbose_name_plural = "Темы статей"


# ──────────────────────────── статья и окружение ─────────────────────────────
class ArticleStatus(models.TextChoices):
    DRAFT = "draft", "Черновик"
    ON_REVIEW = "on_review", "На модерации"
    PUBLISHED = "published", "Опубликована"
    REJECTED = "rejected", "Отклонена"


class Article(models.Model):
    # реакции
    author = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="articles", verbose_name="Автор")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="articles", verbose_name="Категория")
    theme = models.ForeignKey(
        Theme, on_delete=models.SET_NULL, related_name="articles", verbose_name="Тема", **NULLABLE
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")

    # базовые поля
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name="Slug")
    short_description = models.CharField(max_length=250, verbose_name="Краткое описание")
    cover_image = models.ImageField(
        upload_to="articles/covers/", validators=[validate_file_size], verbose_name="Обложка"
    )

    # география
    countries = ArrayField(
        base_field=models.CharField(max_length=2, choices=CountryChoices.choices),
        default=list,
        blank=True,
        verbose_name="Страны",
    )

    # SEO
    meta_title = models.CharField(max_length=255, **NULLABLE, verbose_name="SEO title")
    meta_description = models.CharField(max_length=160, **NULLABLE, verbose_name="SEO description")

    # содержание и метрики
    content = models.TextField(verbose_name="Полный текст статьи")
    rating = models.FloatField(default=0, verbose_name="Рейтинг")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")

    # workflow
    status = models.CharField(
        max_length=15, choices=ArticleStatus.choices, default=ArticleStatus.DRAFT, db_index=True, verbose_name="Статус"
    )
    published_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="Дата публикации")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"], name="status_pub_idx"),
            GinIndex(fields=["countries"], name="countries_gin"),
        ]

    # ─────────────── helpers ───────────────
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:210]
            slug, n = base, 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    # workflow
    def submit_for_review(self):
        self.status = ArticleStatus.ON_REVIEW
        self.save(update_fields=["status"])

    def publish(self):
        self.status = ArticleStatus.PUBLISHED
        if not self.published_at:
            self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at"])

    # computed
    @property
    def is_published(self) -> bool:
        return self.status == ArticleStatus.PUBLISHED

    @property
    def reading_time_minutes(self) -> int:
        words = len(self.content.split())
        return max(1, round(words / 200))

    # perms
    def can_edit(self, user) -> bool:
        return user.is_authenticated and (user.is_staff or self.author_id == user.id)

    def __str__(self) -> str:
        return self.title


# ───────────────────────────── медиа ──────────────────────────────
class MediaType(models.TextChoices):
    IMAGE = "image", "Фото"
    VIDEO = "video", "Видео"


class MediaAsset(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="media", verbose_name="Статья")
    type = models.CharField(max_length=10, choices=MediaType.choices, verbose_name="Тип")
    file = models.FileField(upload_to="articles/media/", validators=[validate_file_size], verbose_name="Файл")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Медиа-файл"
        verbose_name_plural = "Медиа-файлы"
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["article", "order"], name="unique_media_order_per_article"),
        ]

    def clean(self):
        super().clean()
        # 1. Лимит «не более 10 медиафайлов на статью»
        # считаем только при создании
        # проверка готовой функции из валидатора, проще поддерживать
        if self._state.adding:
            enforce_media_limit(self.article)
        # 2. Проверяем размер (и расширение, если видео)
        validate_media_file(
            self.file,
            is_video=self.type == MediaType.VIDEO,
        )

    def __str__(self) -> str:
        return f"{self.get_type_display()} для «{self.article.title}»"


# ──────────────────────── реакции / комментарии ─────────────────────────
class Reaction(models.Model):
    user = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, related_name="reactions", verbose_name="Пользователь"
    )
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="reactions", verbose_name="Статья")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Когда")

    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"
        constraints = [
            models.UniqueConstraint(fields=["user", "article"], name="unique_article_reaction"),
        ]
        indexes = [models.Index(fields=["article", "-created_at"], name="reaction_idx")]

    def __str__(self) -> str:
        return f"Лайк от {self.user} для «{self.article.title}»"


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments", verbose_name="Статья")
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name="comments", verbose_name="Автор")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        verbose_name="Родительский комментарий",
    )
    text = models.TextField(verbose_name="Текст", help_text="Максимум 2000 символов")
    status = models.CharField(
        max_length=10,
        choices=[("pending", "На модерации"), ("approved", "Одобрен"), ("rejected", "Отклонён")],
        default="pending",
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Комментарий #{self.pk} от {self.user}"


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes", verbose_name="Комментарий")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    is_like = models.BooleanField(default=True, verbose_name="Лайк / Дизлайк")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Когда")

    class Meta:
        verbose_name = "Реакция на комментарий"
        verbose_name_plural = "Реакции на комментарии"
        constraints = [
            models.UniqueConstraint(fields=["comment", "user"], name="unique_comment_reaction"),
        ]

    def __str__(self) -> str:
        return "Лайк" if self.is_like else "Дизлайк"
