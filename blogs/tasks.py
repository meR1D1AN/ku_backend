import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from blogs.models import Article

logger = logging.getLogger(__name__)


@shared_task
def send_moderation_notification(article_id):
    """Отправляет уведомление администратору о новой статье, ожидающей модерации."""
    try:
        article = Article.objects.get(pk=article_id)
        message = (
            f"Новая статья '{article.title}' ожидает модерации.  "
            f"Ссылка: {settings.SITE_URL}/admin/blogs/article/{article.id}/change/"
        )
        send_mail(
            subject="Новая статья для модерации",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,  # настройки почтового сервера
            recipient_list=[settings.ADMIN_EMAIL],  # настройки почтового сервера
        )
        logger.info(f"Уведомление о модерации отправлено для статьи {article_id}")
    except Article.DoesNotExist:
        logger.error(f"Статья с ID {article_id} не найдена.")
    except Exception as e:
        logger.exception(f"Ошибка при отправке уведомления о модерации: {e}")
