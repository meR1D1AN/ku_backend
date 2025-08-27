from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

# единый источник констант для drf-spectacular
from all_fixture.views_fixture import (
    ARTICLE_ID,
    BLOG_SETTINGS,
    CATEGORY_ID,
    CATEGORY_SETTINGS,
    COMMENT_Q,
    COMMENTS_SETTINGS,
    COUNTRY,
    LIKE_ID,
    LIKES_SETTINGS,
    LIMIT,
    OFFSET,
    ORDERING,
    PUBLISHED_AT_AFTER,
    PUBLISHED_AT_BEFORE,
    SEARCH,
    TAG_ID,
    TAG_SETTINGS,
    THEME_ID,
    THEME_SETTINGS,
)
from blogs.filters import ArticleFilter
from blogs.models import Article, ArticleStatus, Category, Comment, CommentLike, Tag, Theme
from blogs.permissions import IsAuthorOrAdmin
from blogs.serializers import (
    ArticleSerializer,
    CategorySerializer,
    CommentLikeSerializer,
    CommentSerializer,
    TagSerializer,
    ThemeSerializer,
)


# ─── Справочники ───────────────────────────────────────────────────────────────
@extend_schema_view(
    list=extend_schema(
        summary="Список категорий",
        tags=[CATEGORY_SETTINGS["name"]],
        responses={200: CategorySerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Деталь категории",
        tags=[CATEGORY_SETTINGS["name"]],
        parameters=[CATEGORY_ID],
        responses={200: CategorySerializer, 404: OpenApiResponse(description="Не найдена")},
    ),
)
class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


@extend_schema_view(
    list=extend_schema(
        summary="Список тегов",
        tags=[TAG_SETTINGS["name"]],
        responses={200: TagSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Деталь тега",
        tags=[TAG_SETTINGS["name"]],
        parameters=[TAG_ID],
        responses={200: TagSerializer, 404: OpenApiResponse(description="Не найден")},
    ),
)
class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema_view(
    list=extend_schema(
        summary="Список тем",
        tags=[THEME_SETTINGS["name"]],
        responses={200: ThemeSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Деталь темы",
        tags=[THEME_SETTINGS["name"]],
        parameters=[THEME_ID],
        responses={200: ThemeSerializer, 404: OpenApiResponse(description="Не найдена")},
    ),
)
class ThemeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [permissions.AllowAny]


# ─── Статьи: CRUD + модерация ───────────────────────────────────────────────────
@extend_schema_view(
    list=extend_schema(
        summary="Список статей",
        tags=[BLOG_SETTINGS["name"]],
        parameters=[
            PUBLISHED_AT_AFTER,
            PUBLISHED_AT_BEFORE,
            COUNTRY,
            THEME_ID,
            ORDERING,
            SEARCH,
            LIMIT,
            OFFSET,
        ],
        responses={200: ArticleSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Создать статью",
        tags=[BLOG_SETTINGS["name"]],
        request={"multipart/form-data": ArticleSerializer},
        responses={201: ArticleSerializer, 401: OpenApiResponse(description="Требуется авторизация")},
    ),
    retrieve=extend_schema(
        summary="Деталь статьи",
        tags=[BLOG_SETTINGS["name"]],
        parameters=[ARTICLE_ID],
        responses={200: ArticleSerializer, 404: OpenApiResponse(description="Не найдена")},
    ),
    update=extend_schema(
        summary="Обновить статью",
        tags=[BLOG_SETTINGS["name"]],
        parameters=[ARTICLE_ID],
        request={"multipart/form-data": ArticleSerializer},
        responses={200: ArticleSerializer, 403: OpenApiResponse(description="Запрещено")},
    ),
    destroy=extend_schema(
        summary="Удалить статью",
        tags=[BLOG_SETTINGS["name"]],
        parameters=[ARTICLE_ID],
        responses={204: OpenApiResponse(description="Удалено"), 403: OpenApiResponse(description="Запрещено")},
    ),
    moderate=extend_schema(
        summary="Модерировать статью",
        tags=[BLOG_SETTINGS["name"]],
        parameters=[ARTICLE_ID],
        responses={200: OpenApiResponse(description="Опубликована"), 403: OpenApiResponse(description="Только админ")},
    ),
)
class ArticleViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    http_method_names = ["get", "post", "put", "delete"]

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = ArticleFilter
    ordering_fields = [
        "published_at",
        "-published_at",
        "created_at",
        "-created_at",
        "views_count",
        "-views_count",
        "rating",
        "-rating",
    ]
    search_fields = ["title", "content", "tags__name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        if self.action in ("moderate",):
            return [permissions.IsAdminUser()]
        return [IsAuthorOrAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        return qs if user.is_staff else qs.filter(status=ArticleStatus.PUBLISHED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, status=ArticleStatus.DRAFT)

    # ─── Действия пользователя ─────────────────────────────────────────────────────
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Автор отправляет статью на модерацию."""
        article = self.get_object()
        self.check_object_permissions(request, article)
        article.submit_for_review()
        return Response({"status": article.status})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def moderate(self, request, pk=None):
        """Админ публикует или отклоняет статью."""
        article = self.get_object()
        if request.data.get("action") == "reject":
            article.status = ArticleStatus.REJECTED
            article.save(update_fields=["status"])
        else:  # publish по умолчанию
            article.publish()
        return Response({"status": article.status})


# ─── Комментарии и реакции ─────────────────────────────────────────────────────
@extend_schema_view(
    list=extend_schema(
        summary="Список комментариев",
        tags=[COMMENTS_SETTINGS["name"]],
        parameters=[LIMIT, OFFSET],
        responses={200: CommentSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Добавить комментарий",
        tags=[COMMENTS_SETTINGS["name"]],
        request=CommentSerializer,
        responses={201: CommentSerializer, 401: OpenApiResponse(description="Требуется авторизация")},
    ),
)
class CommentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Comment.objects.filter(status="approved")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status="pending")


@extend_schema_view(
    list=extend_schema(
        summary="Список реакций на комментарии",
        tags=[LIKES_SETTINGS["name"]],
        parameters=[COMMENT_Q, LIMIT, OFFSET],
        responses={200: CommentLikeSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Поставить или изменить реакцию",
        tags=[LIKES_SETTINGS["name"]],
        request=CommentLikeSerializer,
        responses={201: CommentLikeSerializer, 401: OpenApiResponse(description="Требуется авторизация")},
    ),
    destroy=extend_schema(
        summary="Удалить реакцию",
        tags=[LIKES_SETTINGS["name"]],
        parameters=[LIKE_ID],
        responses={204: OpenApiResponse(description="Удалено"), 403: OpenApiResponse(description="Только владелец")},
    ),
)
class CommentLikeViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CommentLikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CommentLike.objects.none()

    def get_queryset(self):
        request: Request = self.request
        qs = CommentLike.objects.filter(user=request.user)
        comment_id = request.query_params.get("comment")
        if comment_id:
            qs = qs.filter(comment_id=comment_id)
        return qs

    def perform_create(self, serializer):
        comment = serializer.validated_data["comment"]
        CommentLike.objects.filter(user=self.request.user, comment=comment).delete()
        serializer.save(user=self.request.user)
