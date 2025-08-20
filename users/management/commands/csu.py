import os

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Создание суперпользователя"""

    def handle(self, *args, **options):
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")

        try:
            user = User.objects.create(
                email=email,
                is_staff=True,
                is_superuser=True,
            )
            user.set_password(password)
            user.save()
        except Exception:
            self.stdout.write(self.style.ERROR("SUPERUSER CREATE FAILED"))
        else:
            self.stdout.write(self.style.SUCCESS("SUPERUSER CREATE SUCCESS"))
