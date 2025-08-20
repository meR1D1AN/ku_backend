from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from blogs.views import (
    ArticleViewSet,
    CategoryViewSet,
    CommentLikeViewSet,
    CommentViewSet,
    TagViewSet,
    ThemeViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"themes", ThemeViewSet, basename="theme")
router.register(r"articles", ArticleViewSet, basename="article")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"comment-likes", CommentLikeViewSet, basename="comment-like")

urlpatterns = [
    path("", include(router.urls)),
]

# ─── раздача медиа-файлов в режиме DEBUG ─────────────────────────────
# избегаем лишних URL в проде
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
