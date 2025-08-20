from celery import shared_task
from django.core.mail import send_mail

import users
from users.models import User


@shared_task
def clear_user_password(user_id):
    """Удаление пароля через 5 минут после назначения"""

    try:
        user = User.objects.get(id=user_id)
    except users.models.User.DoesNotExist:
        pass
    else:
        user.set_password("")
        user.save(update_fields=["password"])


@shared_task
def send_message(subject, message, from_email, recipient_list):
    """
    Отправка письма
    """

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
    )
