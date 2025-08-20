import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = "redis://redis:6379/0"  # Указываем Redis как брокер
app.conf.result_backend = "redis://redis:6379/0"
app.autodiscover_tasks()
