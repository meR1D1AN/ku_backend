from __future__ import annotations

from typing import Any

from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from all_fixture.choices import CountryChoices
from blogs.models import (
    Article,
    Category,
    Comment,
    CommentLike,
    MediaAsset,
    MediaType,
    Tag,
    Theme,
)
from blogs.validators import (
    DynamicForbiddenWordValidator,
    enforce_media_limit,
    validate_media_file,
)


# ────────────────────────── базовые справочники ──────────────────────────
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ("id", "name", "slug")


# ───────────────────────────── медиа-файлы ────────────────────────────────
class MediaAssetSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = MediaAsset
        fields = ("id", "article", "type", "file", "order")
        read_only_fields = ("id",)

    # валидация на уровне объекта
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        article = data.get("article") or getattr(self.instance, "article", None)

        # 1. лимит 10 файлов
        if self.instance is None and article is not None:
            enforce_media_limit(article)

        # 2. размер + расширение
        validate_media_file(
            data["file"],
            is_video=data["type"] == MediaType.VIDEO,
        )
        return data


# ─────────────────────────── комментарии / лайки ──────────────────────────
class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ("id", "comment", "user", "is_like", "created_at")
        read_only_fields = ("id", "user", "created_at")


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "article",
            "user",
            "parent",
            "text",
            "replies",
            "likes_count",
            "dislikes_count",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "replies",
            "likes_count",
            "dislikes_count",
            "created_at",
            "updated_at",
        )

    # рекурсивная выдача ответов (до 2-го уровня)
    def get_replies(self, obj):
        depth = self.context.get("depth", 0)
        if depth >= 2:
            return []
        qs = Comment.objects.filter(parent=obj, status="approved")
        ctx = {**self.context, "depth": depth + 1}
        return CommentSerializer(qs, many=True, context=ctx).data

    @staticmethod
    def get_likes_count(obj):  # noqa: D401
        return obj.likes.filter(is_like=True).count()

    @staticmethod
    def get_dislikes_count(obj):  # noqa: D401
        return obj.likes.filter(is_like=False).count()


# ─────────────────────────────── статьи ──────────────────────────────────
class ArticleSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    tags = TagSerializer(many=True, required=False)
    theme = ThemeSerializer(required=False, allow_null=True)
    media = MediaAssetSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    author = serializers.HiddenField(default=CurrentUserDefault())
    reading_time = serializers.IntegerField(source="reading_time_minutes", read_only=True)

    countries = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Список русских названий стран",
    )

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "meta_title",
            "meta_description",
            "cover_image",
            "countries",
            "rating",
            "status",
            "views_count",
            "reading_time",
            "content",
            "category",
            "tags",
            "theme",
            "author",
            "media",
            "comments",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "slug",
            "status",
            "views_count",
            "reading_time",
            "rating",
            "created_at",
            "updated_at",
            "media",
            "comments",
        )

    # ─── валидаторы «плохих слов» ─────────────────────────────────────────
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        banned = DynamicForbiddenWordValidator()
        self.fields["title"].validators.append(banned)
        self.fields["content"].validators.append(banned)

    # ─── страны: валидация и маппинг код ⇄ рус. название ──────────────────
    def validate_countries(self, value):
        valid_names = {name for _, name in CountryChoices.choices}
        unknown = [n for n in value if n not in valid_names]
        if unknown:
            raise serializers.ValidationError(f"Неизвестные страны: {', '.join(unknown)}")
        return value

    def to_internal_value(self, data):
        mapping = {name: code for code, name in CountryChoices.choices}
        if "countries" in data:
            data["countries"] = [mapping[n] for n in data["countries"] if n in mapping]
        return super().to_internal_value(data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rev = dict(CountryChoices.choices)
        rep["countries"] = [rev.get(code, code) for code in rep.get("countries", [])]
        return rep

    # ─── nested create/update ─────────────────────────────────────────────
    def _get_or_create_tag(self, tag_dict):
        return Tag.objects.get_or_create(**tag_dict)[0]

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        category_data = validated_data.pop("category")
        theme_data = validated_data.pop("theme", None)

        category, _ = Category.objects.get_or_create(**category_data)
        theme = Theme.objects.get_or_create(**theme_data)[0] if theme_data else None

        article = Article.objects.create(
            category=category,
            theme=theme,
            **validated_data,
        )
        # теги
        article.tags.set(self._get_or_create_tag(t) for t in tags_data)
        return article

    def update(self, instance, validated_data):
        if "category" in validated_data:
            cat_data = validated_data.pop("category")
            instance.category, _ = Category.objects.get_or_create(**cat_data)

        if "theme" in validated_data:
            theme_data = validated_data.pop("theme")
            instance.theme = Theme.objects.get_or_create(**theme_data)[0] if theme_data else None

        if "tags" in validated_data:
            instance.tags.set(self._get_or_create_tag(t) for t in validated_data.pop("tags"))

        # остальные простые поля
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance
